import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app import models
from app.routers.auth_router import router as auth_router
from app.routers.company_router import router as company_router
from app.routers.log_router import router as log_router
from app.routers.personnel_router import router as personnel_router
from app.routers.scraper_router import router as scraper_router
from app.routers.search_router import router as search_router
from app.routers.reports_router import router as reports_router

# Ensure database tables exist on startup
models.Base.metadata.create_all(bind=engine)

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

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(scraper_router, prefix="/api/v1/scraper", tags=["scraper"])
app.include_router(company_router, prefix="/api/v1", tags=["companies"])
app.include_router(personnel_router, prefix="/api/v1", tags=["personnel"])
app.include_router(log_router, prefix="/api/v1", tags=["logs"])
app.include_router(search_router, prefix="/api/v1", tags=["search"])
app.include_router(reports_router, prefix="/api/v1", tags=["reports"])
