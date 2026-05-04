@echo off
echo ================================================
echo   RFID Pristina — Demarrage serveur Flask
echo ================================================
echo.
echo Installation des dependances...
pip install -r requirements.txt -q
echo.
echo Demarrage du serveur...
echo Dashboard : http://localhost:5000
echo.
python backend/app.py
pause
