import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analiz import AnalizMotoru


def test_clean_text_for_llm_removes_boilerplate() -> None:
    motor = AnalizMotoru()
    text = (
        "<header>Menu</header> Bu şirket, <script>var x=1;</script> güçlü bir yazılım ekibine sahip. "
        "İlgili link: https://example.com/contact privacy policy bilgiler. Footer bilgisi burada."
    )

    cleaned = motor._clean_text_for_llm(text)

    assert "menu" not in cleaned.lower()
    assert "https://example.com/contact" not in cleaned
    assert "privacy policy" not in cleaned.lower()
    assert "script" not in cleaned.lower()
    assert "footer" not in cleaned.lower()
    assert "güçlü bir yazılım ekibine sahip" in cleaned


def test_analiz_et_filters_elite_companies() -> None:
    motor = AnalizMotoru()
    motor.model = MagicMock()
    motor.model.generate_content.return_value = MagicMock(
        text='''[
            {"name":"Elit Yazılım","website":"https://elit.com","location":"İstanbul","description":"Yapay zeka platformu","source":"web","confidence_score":90},
            {"name":"Düşük Güven","website":"https://dusuk.com","location":"Ankara","description":"Hizmet sağlayıcı","source":"web","confidence_score":70}
        ]'''
    )

    result = asyncio.run(motor.analiz_et("Bu metin şirket bilgilerini içeriyor."))

    assert isinstance(result, list)
    assert any(item["name"] == "Elit Yazılım" for item in result)
    assert any(item["name"] == "Düşük Güven" for item in result)
    assert all(0 <= item["confidence_score"] <= 100 for item in result)

    # 5. Gün hedefi için eklediğimiz yeni kontrol:
    # LLM çıktısından sadece 85 ve üzeri güven skoruna sahip olanları filtrelediğinden emin ol
    elite_results = [item for item in result if item["confidence_score"] >= 85]
    
    # Bu testin başarılı olması için "Elit Yazılım"ın (90 puan) listede olması, 
    # "Düşük Güven"in (70 puan) ise filtrede elenmesi gerekir:
    assert len(elite_results) == 1
    assert elite_results[0]["name"] == "Elit Yazılım"


def test_analiz_et_invalid_json_returns_fallback() -> None:
    motor = AnalizMotoru()
    motor.model = MagicMock()
    motor.model.generate_content.return_value = MagicMock(text='invalid json response')

    result = asyncio.run(motor.analiz_et("Karmaşık metin buraya.") )

    assert isinstance(result, list)
    assert result[0].get("hata") == "JSON_PARSE_ERROR"
    assert result[0]["name"] == "Belirsiz"
