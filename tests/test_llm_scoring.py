import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from analiz import AnalizMotoru


def _response(content: str) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def test_clean_text_for_llm_removes_boilerplate() -> None:
    motor = AnalizMotoru()
    cleaned = motor._clean_text_for_llm(
        "<header>Menü</header><script>var x=1;</script>"
        "Güçlü bir CNC üreticisidir. https://example.com privacy policy"
    )

    assert "menü" not in cleaned.lower()
    assert "script" not in cleaned.lower()
    assert "https://" not in cleaned
    assert "privacy policy" not in cleaned.lower()
    assert "CNC üreticisidir" in cleaned


def test_analysis_posts_only_high_confidence_companies_with_context() -> None:
    motor = AnalizMotoru()
    motor.client = MagicMock()
    motor.client.chat.completions.create = AsyncMock(
        return_value=_response(
            '[{"name":"Elit CNC","location":"İstanbul",'
            '"description":"CNC freze üretimi","source":"web",'
            '"confidence_score":92,"officials":[]},'
            '{"name":"Zayıf Aday","location":"Ankara",'
            '"description":"Belirsiz","source":"web",'
            '"confidence_score":60,"officials":[]}]'
        )
    )
    motor._post_companies_to_api_async = AsyncMock()

    results = asyncio.run(
        motor.analiz_et(
            "İstanbul CNC firma metni",
            search_history_id=7,
            source_url="https://example.com/cnc",
        )
    )

    assert len(results) == 2
    posted = motor._post_companies_to_api_async.await_args.args[0]
    assert [item["name"] for item in posted] == ["Elit CNC"]
    assert motor._post_companies_to_api_async.await_args.kwargs == {
        "search_history_id": 7,
        "source_url": "https://example.com/cnc",
    }


def test_invalid_llm_json_returns_controlled_fallback() -> None:
    motor = AnalizMotoru()
    motor.client = MagicMock()
    motor.client.chat.completions.create = AsyncMock(
        return_value=_response("geçersiz json")
    )

    result = asyncio.run(motor.analiz_et("Firma metni"))

    assert result[0]["name"] == "Belirsiz"
    assert result[0]["confidence_score"] == 50


def test_empty_text_does_not_call_llm() -> None:
    motor = AnalizMotoru()
    motor.client = MagicMock()

    result = asyncio.run(motor.analiz_et("   "))

    assert result[0]["hata"] == "Boş metin"
    motor.client.chat.completions.create.assert_not_called()
