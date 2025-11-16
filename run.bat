@echo off
cd /d "%~dp0"
echo ========================================
echo   HELIOS - Servidor Flask
echo ========================================
echo.
echo Iniciando servidor na porta 5000...
echo Acesse: http://localhost:5000
echo Usuario: admin
echo Senha: admin123
echo.
echo Pressione Ctrl+C para parar o servidor
echo.
python app.py
pause


