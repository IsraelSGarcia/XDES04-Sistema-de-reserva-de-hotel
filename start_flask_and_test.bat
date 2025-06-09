@echo off
echo ========================================
echo RESTEL - Iniciando Flask e Testes
echo ========================================

echo 🚀 Iniciando aplicacao Flask...
start "Flask RESTEL" cmd /k "python app.py"

echo ⏰ Aguardando Flask inicializar...
timeout /t 5 /nobreak >nul

echo 🧪 Iniciando testes automatizados...
python run_tests.py --visible

echo ✅ Testes concluidos!
pause 