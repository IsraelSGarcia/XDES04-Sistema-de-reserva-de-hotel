@echo off
echo ========================================
echo RESTEL - Comandos de Teste Automatizado
echo ========================================
echo.

echo 1. Instalar dependencias
echo    python run_tests.py --install-deps
echo.

echo 2. Executar todos os testes
echo    python run_tests.py
echo.

echo 3. Executar testes de hospedes
echo    python run_tests.py --type guest
echo.

echo 4. Executar testes de administradores
echo    python run_tests.py --type admin
echo.

echo 5. Executar com browser visivel
echo    python run_tests.py --visible
echo.

echo 6. Executar com verificacao do Flask
echo    python run_tests.py --check-flask
echo.

echo 7. Executar testes especificos com pytest
echo    pytest tests/test_guest_crud.py -v
echo    pytest tests/test_admin_crud.py -v
echo.

echo 8. Gerar relatorio HTML
echo    pytest tests/ --html=reports/report.html --self-contained-html
echo.

echo ========================================
echo Escolha o comando que deseja executar
echo ========================================

:menu
set /p choice="Digite o numero do comando (1-8) ou 'q' para sair: "

if "%choice%"=="1" (
    python run_tests.py --install-deps
    goto menu
)
if "%choice%"=="2" (
    python run_tests.py
    goto menu
)
if "%choice%"=="3" (
    python run_tests.py --type guest
    goto menu
)
if "%choice%"=="4" (
    python run_tests.py --type admin
    goto menu
)
if "%choice%"=="5" (
    python run_tests.py --visible
    goto menu
)
if "%choice%"=="6" (
    python run_tests.py --check-flask
    goto menu
)
if "%choice%"=="7" (
    set /p testfile="Digite o arquivo de teste (guest/admin): "
    if "%testfile%"=="guest" pytest tests/test_guest_crud.py -v
    if "%testfile%"=="admin" pytest tests/test_admin_crud.py -v
    goto menu
)
if "%choice%"=="8" (
    pytest tests/ --html=reports/report.html --self-contained-html
    goto menu
)
if "%choice%"=="q" (
    echo Saindo...
    exit /b
)

echo Opcao invalida. Tente novamente.
goto menu 