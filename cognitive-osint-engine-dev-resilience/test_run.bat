@echo off
echo ===================================================
echo    OTOMATIK OSINT MOTORU TESTI BASLATILIYOR
echo ===================================================
echo.

echo [1/3] FastAPI Backend Baslatiliyor (Port 8000)...
start "1 - FastAPI Backend" cmd /k "call .venv\Scripts\activate.bat & cd autonomous-osint-agent\core-api & python -m uvicorn app.main:app --reload"

:: Sunucunun açılması için 3 saniye bekleniyor
timeout /t 3 /nobreak >nul

echo [2/3] Redis Dinleyicisi Baslatiliyor (Veri Bekleniyor)...
start "2 - Redis Listener" cmd /k "call .venv\Scripts\activate.bat & python redis_listener.py"

:: 2 saniye bekleniyor
timeout /t 2 /nobreak >nul

echo [3/3] Scraper Botlari Baslatiliyor (Denizli Tekstil)...
start "3 - Scraper Bots" cmd /k "call .venv\Scripts\activate.bat & cd scraper-bot & python main.py --sorgu ""Denizli Tekstil"""
echo.
echo Tamamlandi! 3 ayri pencere acildi.
echo Bu ana pencereyi kapatabilirsiniz.