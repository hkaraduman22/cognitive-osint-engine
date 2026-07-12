import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, ensure_mvp_schema
from app import models
from app.controllers.admin_controller import router as admin_router
from app.controllers.auth_controller import router as auth_router
from app.controllers.search_controller import router as search_router
from app.routers.company_router import router as company_router
from app.routers.log_router import router as log_router
from app.routers.personnel_router import router as personnel_router

# Ensure database tables exist on startup
models.Base.metadata.create_all(bind=engine)
ensure_mvp_schema()

# Configure root logging so module loggers (logger.info/err) are visible in uvicorn output
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="OSINT Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(search_router, prefix="/api/v1/search", tags=["search"])
# NOT: /api/v1/scraper/scan (scraper_router) kasitli olarak mount edilmiyor.
# search_history_id parametresi olmadan tarama tetikliyordu, bu yuzden urettigi
# sonuclar hicbir aramada (GET /companies?arama_id=X) gorunmuyordu - kafa karistirici
# ve gereksiz bir ikinci tarama yolu idi. Gercek/tam ozellikli tarama yolu:
# POST /api/v1/companies/scan (company_router).
app.include_router(company_router, prefix="/api/v1", tags=["companies"])
app.include_router(personnel_router, prefix="/api/v1", tags=["personnel"])
app.include_router(log_router, prefix="/api/v1", tags=["logs"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["admin"])
