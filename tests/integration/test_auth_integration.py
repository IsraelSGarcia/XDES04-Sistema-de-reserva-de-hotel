"""
Testes de Integração - Autenticação RESTEL
Testes de fluxos completos de autenticação e autorização
"""

import pytest
import sqlite3


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.smoke
def test_admin_login_flow(app_client, admin_credentials, clean_database):
    """Testa fluxo completo de login do administrador"""
    # 1. Acessar página de login
    response = app_client.get('/admin/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()
    
    # 2. Fazer login com credenciais corretas
    response = app_client.post('/admin/login', data=admin_credentials)
    assert response.status_code in [200, 302]
    
    # 3. Verificar se foi redirecionado para painel
    if response.status_code == 302:
        assert '/admin/painel' in response.location or '/admin' in response.location
    
    # 4. Acessar painel admin
    response = app_client.get('/admin/painel')
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.auth
def test_guest_registration_login_flow(app_client, valid_guest_data, clean_database):
    """Testa fluxo completo de cadastro e login de hóspede"""
    # 1. Cadastrar novo hóspede
    response = app_client.post('/cadastro', data=valid_guest_data)
    assert response.status_code in [200, 302]
    
    # 2. Fazer login com dados cadastrados
    login_data = {
        'email': valid_guest_data['email'],
        'senha': valid_guest_data['senha']
    }
    
    response = app_client.post('/login', data=login_data)
    assert response.status_code in [200, 302]
    
    # 3. Verificar se foi redirecionado para painel do hóspede
    if response.status_code == 302:
        assert '/painel' in response.location or '/hospede' in response.location


@pytest.mark.integration
@pytest.mark.auth
def test_invalid_login_attempts(app_client, invalid_credentials):
    """Testa tentativas de login com credenciais inválidas"""
    # Login admin inválido
    response = app_client.post('/admin/login', data=invalid_credentials)
    assert response.status_code in [200, 400, 401]
    
    # Login hóspede inválido
    response = app_client.post('/login', data=invalid_credentials)
    assert response.status_code in [200, 400, 401]


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.database
def test_password_hashing(app_client, valid_guest_data, test_database):
    """Testa se senhas são hash corretamente no banco"""
    # Cadastrar hóspede
    app_client.post('/cadastro', data=valid_guest_data)
    
    # Verificar no banco que senha não está em texto plano
    conn = sqlite3.connect(test_database)
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT senha FROM hospedes WHERE email = ?", 
        (valid_guest_data['email'],)
    )
    result = cursor.fetchone()
    
    assert result is not None
    stored_password = result[0]
    
    # Senha armazenada deve ser diferente da original (hash)
    assert stored_password != valid_guest_data['senha']
    # Deve ter características de hash (comprimento, caracteres)
    assert len(stored_password) > 20
    
    conn.close()


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.crud
def test_duplicate_email_registration(app_client, valid_guest_data, clean_database):
    """Testa se não permite cadastrar emails duplicados"""
    # Primeiro cadastro
    response = app_client.post('/cadastro', data=valid_guest_data)
    assert response.status_code in [200, 302]
    
    # Segundo cadastro com mesmo email
    response = app_client.post('/cadastro', data=valid_guest_data)
    # Deve rejeitar ou mostrar erro
    assert response.status_code in [200, 400, 409]
    
    # Se retornou 200, deve ter mensagem de erro
    if response.status_code == 200:
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        error_keywords = ['já existe', 'duplicado', 'erro', 'inválido']
        assert any(keyword in response_text for keyword in error_keywords)


@pytest.mark.integration
@pytest.mark.auth
def test_logout_functionality(logged_admin_client):
    """Testa funcionalidade de logout"""
    # Verificar que está logado (pode acessar painel)
    response = logged_admin_client.get('/admin/painel')
    assert response.status_code == 200
    
    # Fazer logout
    response = logged_admin_client.get('/admin/logout')
    assert response.status_code in [200, 302]
    
    # Tentar acessar painel novamente (deve ser rejeitado)
    response = logged_admin_client.get('/admin/painel')
    # Deve redirecionar para login ou mostrar erro
    assert response.status_code in [302, 401, 403]


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.validation
def test_session_persistence(app_client, admin_credentials):
    """Testa se sessão persiste entre requisições"""
    # Fazer login
    response = app_client.post('/admin/login', data=admin_credentials)
    assert response.status_code in [200, 302]
    
    # Fazer múltiplas requisições para verificar sessão
    for _ in range(3):
        response = app_client.get('/admin/painel')
        assert response.status_code == 200
        
        # Pequena operação para verificar sessão ativa
        response = app_client.get('/admin/hospedes')
        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.validation
def test_input_validation_registration(app_client, invalid_guest_data):
    """Testa validação de dados no cadastro"""
    response = app_client.post('/cadastro', data=invalid_guest_data)
    
    # Deve rejeitar dados inválidos
    assert response.status_code in [200, 400]
    
    # Se retornou 200, deve mostrar mensagens de erro
    if response.status_code == 200:
        response_text = response.data.decode('utf-8', errors='ignore').lower()
        # Pelo menos uma validação deve falhar
        validation_keywords = ['erro', 'inválido', 'obrigatório', 'required']
        assert any(keyword in response_text for keyword in validation_keywords)


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.slow
def test_concurrent_logins(app_client, admin_credentials):
    """Testa múltiplos logins simultâneos"""
    import threading
    import time
    
    results = []
    
    def do_login():
        try:
            response = app_client.post('/admin/login', data=admin_credentials)
            results.append(response.status_code)
        except Exception as e:
            results.append(str(e))
    
    # Criar múltiplas threads para login simultâneo
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=do_login)
        threads.append(thread)
    
    # Iniciar todas as threads
    for thread in threads:
        thread.start()
    
    # Aguardar conclusão
    for thread in threads:
        thread.join()
    
    # Verificar que pelo menos algumas tentativas foram bem-sucedidas
    success_codes = [200, 302]
    successful_logins = sum(1 for result in results if result in success_codes)
    assert successful_logins >= 1 