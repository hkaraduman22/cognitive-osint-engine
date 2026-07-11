import json
import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRAPER_PATH = PROJECT_ROOT / "scraper-bot"


def test_message_is_shared_between_separate_processes(tmp_path: Path) -> None:
    queue_db = tmp_path / "process_queue.db"
    environment = os.environ.copy()
    environment["OSINT_QUEUE_DB"] = str(queue_db)
    environment["PYTHONPATH"] = str(SCRAPER_PATH)

    producer_code = (
        "from core.sqlite_queue import SQLiteMessageQueue; "
        "SQLiteMessageQueue().push('osint_raw_queue', "
        "'{\"ham_metin\": \"CNC üreticisi\"}')"
    )
    subprocess.run(
        [sys.executable, "-c", producer_code],
        env=environment,
        check=True,
        cwd=PROJECT_ROOT,
    )

    consumer_code = (
        "from core.sqlite_queue import SQLiteMessageQueue; "
        "print(SQLiteMessageQueue().pop('osint_raw_queue'))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", consumer_code],
        env=environment,
        check=True,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )

    payload = json.loads(completed.stdout.strip())
    assert payload["ham_metin"] == "CNC üreticisi"
