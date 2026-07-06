import argparse
from core.storage import RamDataStorage
from core.coordinator import DataDrivenCoordinator
from spiders.html_parser import GeneralHtmlParser
from analiz import AnalizMotoru

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-Source OSINT Data-Driven Engine")
    parser.add_argument(
        "--sorgu",
        type=str,
        required=True,
        help="Aranacak anahtar kelime, sektör veya lokasyon kriteri (Örn: 'Tekstil Denizli')"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    storage = RamDataStorage()
    parser = GeneralHtmlParser()
    ai_engine = AnalizMotoru()

    coordinator = DataDrivenCoordinator(parser=parser, storage=storage, ai_engine=ai_engine)
    coordinator.execute(args.sorgu)

    # -----------------------------------------------------------------
    # GELİŞTİRİCİ TEST ÇIKTILARI (Sadece senin debug yapman için var)
    # -----------------------------------------------------------------
    veriler = storage.get_all()
    print("\n" + "=" * 70)
    print(f" TARAMA TAMAMLANDI | RAM Bellekteki Toplam Firma Kaydı: {len(veriler)}")
    print("=" * 70)

    for i, veri in enumerate(veriler, 1):
        print(f"\n{i}. [{veri['kaynak'].upper()}] -> {veri['hedef_url']}")
        print(f"   E-postalar : {veri['iletisim_bilgileri']['e_postalar']}")
        print(f"   Telefonlar : {veri['iletisim_bilgileri']['telefonlar']}")
        print(f"   AI Analizi : {veri['ai_analizi']}")
        print(f"   Metin (İlk 150 Karakter): {veri['ham_metin'][:150]}...")
    print("=" * 70)


if __name__ == "__main__":
    main()