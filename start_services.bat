@echo off
echo ===================================================
echo    OSINT ARKA PLAN SERVISLERI BASLATILIYOR
echo ===================================================
echo.

:: 1. FastAPI Backend Sunucusunu Baslat
echo [1/2] FastAPI Backend Baslatiliyor (Port 8000)...
start "FastAPI Backend" cmd /k "call .venv\Scripts\activate.bat && cd autonomous-osint-agent\core-api && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

:: Sunucunun hazir hale gelmesi icin 3 saniye bekleme süresi
timeout /t 3 /nobreak >nul

:: 2. Canli Ortam Redis Dinleyicisini (Listener) Baslat
echo [2/2] Redis Dinleyicisi Baslatiliyor...
start "Redis Listener" cmd /k "call .venv\Scripts\activate.bat && python redis_listener.py"

echo.
echo ===================================================
echo    SERVISLER AKTIF! UI UYGULAMASINI KULLANABILIRSINIZ
echo ===================================================
timeout /t 2 /nobreak >nul
exit