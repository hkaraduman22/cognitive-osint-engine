import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from analiz import AnalizMotoru


async def run_case(name: str, text: str) -> None:
    motor = AnalizMotoru()
    result = await motor.analiz_et(text)
    print(f"\n[{name}]")
    print(result)
    print("-" * 60)


async def main() -> None:
    await run_case(
        "case_1_llm",
        "ABC Teknoloji'nin kurucu ortağı Ahmet Yılmaz, 15 yıllık yazılım deneyimine sahip. "
        "Şirketin CEO'su ve yapay zeka departmanının lideridir.",
    )
    await run_case(
        "case_2_fallback",
        "Bu metin çok kısa ve net bir kişi bilgisi içermiyor.",
    )


if __name__ == "__main__":
    asyncio.run(main())
