import argparse
from core.storage import RedisDataStorage
from core.coordinator import DataDrivenCoordinator
from spiders.html_parser import GeneralHtmlParser

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-Source OSINT Data-Driven Engine")
    parser.add_argument("--sorgu", type=str, required=True, help="Aranacak kelime")
    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    storage = RedisDataStorage()
    parser = GeneralHtmlParser()

    coordinator = DataDrivenCoordinator(parser=parser, storage=storage)
    coordinator.execute(args.sorgu)

    print("\n[!] Tarama bitti. Veriler Redis 'osint_raw_queue' kuyruğuna gönderildi.")

if __name__ == "__main__":
    main()