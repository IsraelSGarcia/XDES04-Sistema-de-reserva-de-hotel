"""
Fixtures de Autenticação - Sistema RESTEL
Fixtures para login, sessões e permissões
"""

import pytest
from pathlib import Path
import sys

# O path já é configurado pelo conftest.py raiz


@pytest.fixture
def admin_credentials():
    """Credenciais padrão do administrador"""
    return {
        'email': 'admin@restel.com',
        'senha': 'admin123'
    }


@pytest.fixture
def guest_credentials():
    """Credenciais de exemplo para hóspede"""
    return {
        'email': 'hospede.teste@email.com',
        'senha': 'senha123'
    }


# app_client fixture is defined in main conftest.py


@pytest.fixture
def logged_admin_client(app_client, admin_credentials):
    """Cliente com sessão de admin logado"""
    # Fazer login do admin
    response = app_client.post('/admin/login', data=admin_credentials)
    assert response.status_code in [200, 302]
    
    yield app_client


@pytest.fixture
def logged_guest_client(app_client, guest_credentials, clean_database):
    """Cliente com sessão de hóspede logado"""
    # Primeiro criar o hóspede
    guest_data = {
        'nome_completo': 'Hóspede Teste',
        'email': guest_credentials['email'],
        'cpf': '12345678901',
        'telefone': '(11) 99999-8888',
        'senha': guest_credentials['senha']
    }
    
    # Cadastrar hóspede
    app_client.post('/cadastro', data=guest_data)
    
    # Fazer login
    response = app_client.post('/login', data=guest_credentials)
    assert response.status_code in [200, 302]
    
    yield app_client


@pytest.fixture
def invalid_credentials():
    """Credenciais inválidas para testes de falha"""
    return {
        'email': 'usuario@inexistente.com',
        'senha': 'senha_errada'
    } 