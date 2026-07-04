from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Base sınıfını engine ile birlikte içe aktar
from app.database import engine, Base
from app import models
from app.routers.auth_router import router as auth_router
from app.routers.company_router import router as company_router
from app.routers.log_router import router as log_router
from app.routers.personnel_router import router as personnel_router
from app.routers.scraper_router import router as scraper_router

# 2. models.Base yerine doğrudan Base kullan
Base.metadata.create_all(bind=engine)

app = FastAPI(title="OSINT Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(scraper_router, prefix="/api/v1/scraper", tags=["scraper"])
app.include_router(company_router, prefix="/api/v1", tags=["companies"])
app.include_router(personnel_router, prefix="/api/v1", tags=["personnel"])
app.include_router(log_router, prefix="/api/v1", tags=["logs"])
