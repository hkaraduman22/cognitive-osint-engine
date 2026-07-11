import os
import sys
import tempfile
import uuid
from pathlib import Path


CORE_API_PATH = Path(__file__).resolve().parents[1] / "autonomous-osint-agent" / "core-api"
if str(CORE_API_PATH) not in sys.path:
    sys.path.insert(0, str(CORE_API_PATH))

database_path = Path(tempfile.gettempdir()) / f"camart_api_test_{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{database_path.as_posix()}"

from fastapi.testclient import TestClient

from app.database import engine
from app.main import app


def test_authenticated_search_to_company_results_flow() -> None:
    with TestClient(app) as client:
        username = f"mvp-{uuid.uuid4().hex}"
        register_response = client.post(
            "/auth/register",
            json={"username": username, "password": "MvpTest123!"},
        )
        assert register_response.status_code == 200
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        search_response = client.post(
            "/api/v1/search/",
            headers=headers,
            json={"query": "İstanbul CNC freze üreticileri"},
        )
        assert search_response.status_code == 202
        search_id = search_response.json()["search_history_id"]

        company_response = client.post(
            "/api/v1/companies",
            json={
                "name": "Faz 3 Örnek CNC",
                "industry": "CNC freze üretimi",
                "city": "İstanbul",
                "source_url": "https://example.test/cnc",
                "confidence_score": 92,
                "search_history_id": search_id,
                "officials": [],
            },
        )
        assert company_response.status_code == 201

        results_response = client.get(
            f"/api/v1/companies?arama_id={search_id}",
            headers=headers,
        )
        assert results_response.status_code == 200
        results = results_response.json()
        assert len(results) == 1
        assert results[0]["name"] == "Faz 3 Örnek CNC"
        assert results[0]["source_url"] == "https://example.test/cnc"

    engine.dispose()
    database_path.unlink(missing_ok=True)
