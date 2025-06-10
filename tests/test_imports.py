#!/usr/bin/env python3
"""
Script para testar se os imports dos testes estão funcionando
"""

import sys
import os
from pathlib import Path

def test_import_fixes():
    """Testa se as correções de import funcionaram"""
    print("🔧 Testando correções de import...")
    
    # Adicionar paths
    project_root = Path(__file__).parent.parent
    app_path = project_root / "src" / "restel"
    
    sys.path.insert(0, str(app_path))
    sys.path.insert(0, str(project_root))
    
    errors = []
    
    # Teste 1: Import das fixtures de data (com Faker opcional)
    try:
        from tests.fixtures.data_fixtures import valid_guest_data
        print("✅ fixtures.data_fixtures - OK")
    except Exception as e:
        print(f"❌ fixtures.data_fixtures - {e}")
        errors.append(str(e))
    
    # Teste 2: Import do conftest principal
    try:
        import tests.conftest
        print("✅ tests.conftest - OK")
    except Exception as e:
        print(f"❌ tests.conftest - {e}")
        errors.append(str(e))
    
    # Teste 3: Verificar se app pode ser importado
    try:
        from app import app
        print("✅ app importado - OK")
    except Exception as e:
        print(f"⚠️  app não encontrado (normal se Flask não estiver rodando) - {e}")
    
    # Teste 4: Import das outras fixtures
    try:
        from tests.fixtures.database_fixtures import test_database
        print("✅ fixtures.database_fixtures - OK")
    except Exception as e:
        print(f"❌ fixtures.database_fixtures - {e}")
        errors.append(str(e))
    
    try:
        from tests.fixtures.auth_fixtures import admin_credentials
        print("✅ fixtures.auth_fixtures - OK")
    except Exception as e:
        print(f"❌ fixtures.auth_fixtures - {e}")
        errors.append(str(e))
    
    # Resultado
    if errors:
        print(f"\n❌ {len(errors)} erros encontrados:")
        for error in errors:
            print(f"   • {error}")
        return False
    else:
        print("\n✅ Todos os imports funcionando corretamente!")
        return True

if __name__ == "__main__":
    success = test_import_fixes()
    sys.exit(0 if success else 1) 