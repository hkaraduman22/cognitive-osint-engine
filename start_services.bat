@echo off
echo ===================================================
echo    COGNITIVE OSINT ENGINE - SERVIS BASLATICI
echo ===================================================
echo.

:: 1. Docker Servislerini Baslat (PostgreSQL ve Redis)
echo [1/3] Veritabani ve Redis Servisleri Baslatiliyor (Docker)...
cd autonomous-osint-agent
call docker-compose up -d postgres redis
cd ..
echo Docker servisleri hazirlanirken 5 saniye bekleniyor...
timeout /t 5 /nobreak >nul

:: 2. FastAPI Backend Sunucusunu Baslat
echo.
echo [2/3] FastAPI Backend Baslatiliyor (Port 8000)...
start "FastAPI Backend" cmd /k "call .venv\Scripts\activate.bat && cd autonomous-osint-agent\core-api && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

:: Sunucunun hazir hale gelmesi icin 3 saniye bekleme süresi
timeout /t 3 /nobreak >nul

:: 3. Canli Ortam Redis Dinleyicisini (Listener) Baslat
echo.
echo [3/3] OSINT Redis Dinleyicisi Baslatiliyor...
start "Redis Listener" cmd /k "call .venv\Scripts\activate.bat && python redis_listener.py"

echo.
echo ===================================================
echo    SERVISLER AKTIF! OSINT UI UYGULAMASINI BASLATIN
echo ===================================================
timeout /t 2 /nobreak >nul
exit