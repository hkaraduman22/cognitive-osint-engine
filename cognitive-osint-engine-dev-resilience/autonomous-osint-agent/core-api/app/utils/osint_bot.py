import threading
import time
from random import randint

from app.repositories.search_repository import SearchRepository


MINIMUM_SCORE = 85


def fetch_osint_data(query: str) -> list[dict]:
    time.sleep(0.5)
    return [
        {"title": f"{query} - kaynak 1", "content": "Örnek içerik 1", "source": "web", "score": randint(50, 100)},
        {"title": f"{query} - kaynak 2", "content": "Örnek içerik 2", "source": "web", "score": randint(50, 100)},
        {"title": f"{query} - kaynak 3", "content": "Örnek içerik 3", "source": "web", "score": randint(50, 100)},
    ]


def evaluate_with_llm(items: list[dict]) -> list[dict]:
    time.sleep(0.5)
    return items


def run_osint_pipeline(user_id: int, query: str, repository: SearchRepository):
    def task():
        repository.save_bot_log(user_id=user_id, query=query, status="started", message="OSINT botu başlatıldı")
        try:
            raw_items = fetch_osint_data(query)
            scored_items = evaluate_with_llm(raw_items)
            elite_items = [item for item in scored_items if item["score"] >= MINIMUM_SCORE]
            for item in elite_items:
                repository.save_record(
                    title=item["title"],
                    content=item["content"],
                    source=item.get("source"),
                    score=item["score"],
                    created_by=user_id,
                )
            repository.save_bot_log(
                user_id=user_id,
                query=query,
                status="completed",
                message=f"{len(elite_items)} adet elit kayıt işlendi",
            )
        except Exception as exc:
            repository.save_bot_log(
                user_id=user_id,
                query=query,
                status="failed",
                message=str(exc),
            )

    thread = threading.Thread(target=task, daemon=True)
    thread.start()
