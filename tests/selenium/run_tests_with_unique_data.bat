@echo off
echo ========================================
echo    RESTEL - Testes Selenium com Dados Unicos
echo ========================================
echo.

echo 1. Verificando se o Flask esta rodando...
curl -s http://localhost:5000 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Flask nao esta rodando!
    echo    Execute: cd src/restel ^&^& python app.py
    echo.
    pause
    exit /b 1
)
echo ✅ Flask esta rodando

echo.
echo 2. Preparando dados unicos para os testes...
python prepare_test_data.py
if %errorlevel% neq 0 (
    echo ❌ Erro ao preparar dados!
    pause
    exit /b 1
)

echo.
echo 3. Dados preparados com sucesso!
echo.
echo 📋 Dados disponíveis:
echo    • Quartos: 201-206 (diferentes tipos)
echo    • Hóspedes: emails @teste.com
echo    • Datas: sempre futuras
echo.
echo 🚀 Agora execute os testes no Selenium IDE:
echo    1. Abra o Selenium IDE
echo    2. Importe o arquivo: Release 01.side
echo    3. Execute as suites ou testes individuais
echo.
echo 📊 Suites disponíveis:
echo    • Suite CRUD Quartos
echo    • Suite Reservas Admin  
echo    • Suite Área Hóspede
echo    • Suite Segurança
echo    • Suite Completa
echo.
pause 