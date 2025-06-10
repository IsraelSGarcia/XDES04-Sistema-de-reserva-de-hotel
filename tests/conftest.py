"""
Configuração raiz para testes - Sistema RESTEL
Este arquivo garante que o PYTHONPATH seja configurado corretamente
"""

import sys
import os
from pathlib import Path

# Configurar PYTHONPATH para encontrar a aplicação
project_root = Path(__file__).parent.parent

# O app.py está na pasta src/restel
app_path = project_root / "src" / "restel" 

# Adicionar paths necessários
sys.path.insert(0, str(app_path))
sys.path.insert(0, str(project_root))

# Configurar variáveis de ambiente para testes
os.environ['FLASK_TESTING'] = 'True'

# Importar configurações dos testes
pytest_plugins = [
    "tests.config.conftest",
] 