import asyncio
from analiz import AnalizMotoru

async def main():
    engine = AnalizMotoru()
    result = await engine.analiz_et("ABC Teknoloji, Türkiye'nin önde gelen yapay zeka şirketidir.")
    print('LLM fallback test result count:', len(result))
    print(result)

if __name__ == '__main__':
    asyncio.run(main())
