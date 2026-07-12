import argparse
from core.storage import QueueDataStorage
from core.coordinator import DataDrivenCoordinator
from spiders.html_parser import GeneralHtmlParser

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Multi-Source OSINT Data-Driven Engine")
    parser.add_argument("--sorgu", type=str, required=True, help="Aranacak kelime")
    parser.add_argument("--search-history-id", type=int, required=False, default=None, help="Opsiyonel SearchHistory kimliği")
    return parser.parse_args()

def main() -> None:
    args = parse_arguments()

    storage = QueueDataStorage()
    parser = GeneralHtmlParser()

    coordinator = DataDrivenCoordinator(parser=parser, storage=storage)
    coordinator.execute(args.sorgu, search_history_id=args.search_history_id)

    print("\n[!] Tarama bitti. Veriler yapılandırılmış OSINT kuyruğuna gönderildi.")

if __name__ == "__main__":
    main()
