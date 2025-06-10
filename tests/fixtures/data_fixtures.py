"""
Fixtures de Dados de Teste - Sistema RESTEL
Dados padronizados para diferentes cenários de teste
"""

import pytest
import random

# Faker já está instalado nos requirements
from faker import Faker  # type: ignore
fake = Faker('pt_BR')


@pytest.fixture
def valid_guest_data():
    """Dados válidos para hóspede"""
    return {
        'nome_completo': 'João Silva Santos',
        'email': 'joao.teste@email.com',
        'cpf': '12345678901',
        'telefone': '(11) 99999-8888',
        'senha': 'senha123'
    }


@pytest.fixture
def invalid_guest_data():
    """Dados inválidos para teste de validação"""
    return {
        'nome_completo': '',  # Nome vazio
        'email': 'email_invalido',  # Email sem @
        'cpf': '123',  # CPF muito curto
        'telefone': '123',  # Telefone inválido
        'senha': '1'  # Senha muito curta
    }


@pytest.fixture
def valid_admin_data():
    """Dados válidos para administrador"""
    return {
        'nome_completo': 'Maria Administradora',
        'email': 'maria.admin@restel.com',
        'senha': 'admin123',
        'perfil': 'Padrão'
    }


@pytest.fixture
def invalid_admin_data():
    """Dados inválidos para administrador"""
    return {
        'nome_completo': '',
        'email': 'email_sem_arroba',
        'senha': '12',  # Muito curta
        'perfil': ''
    }


@pytest.fixture
def random_guest_data():
    """Gera dados aleatórios para hóspede usando Faker"""
    return {
        'nome_completo': fake.name(),
        'email': fake.email(),
        'cpf': fake.cpf().replace('.', '').replace('-', ''),
        'telefone': fake.phone_number(),
        'senha': fake.password(length=8)
    }


@pytest.fixture
def multiple_guests_data():
    """Lista com múltiplos hóspedes para testes em lote"""
    return [
        {
            'nome_completo': 'Ana Costa',
            'email': 'ana.costa@email.com',
            'cpf': '11122233344',
            'telefone': '(11) 98888-7777',
            'senha': 'ana123'
        },
        {
            'nome_completo': 'Carlos Pereira',
            'email': 'carlos.pereira@email.com',
            'cpf': '55566677788',
            'telefone': '(11) 97777-6666',
            'senha': 'carlos123'
        },
        {
            'nome_completo': 'Diana Oliveira',
            'email': 'diana.oliveira@email.com',
            'cpf': '99988877766',
            'telefone': '(11) 96666-5555',
            'senha': 'diana123'
        }
    ]


@pytest.fixture
def edge_case_data():
    """Dados para casos extremos"""
    return {
        'nome_muito_longo': 'A' * 256,  # Nome muito longo
        'email_muito_longo': 'a' * 250 + '@email.com',
        'cpf_com_pontuacao': '123.456.789-00',
        'telefone_com_parenteses': '(11) 99999-8888',
        'senha_com_espacos': ' senha com espaços ',
        'caracteres_especiais': 'João José da Silva-Santos'
    }


@pytest.fixture
def sql_injection_data():
    """Dados para teste de SQL injection"""
    return {
        'nome_completo': "'; DROP TABLE hospedes; --",
        'email': "test@test.com'; DELETE FROM administradores; --",
        'cpf': "'; UNION SELECT * FROM administradores; --",
        'telefone': "'; UPDATE hospedes SET senha='hack'; --",
        'senha': "'; INSERT INTO administradores VALUES('hack'); --"
    }


@pytest.fixture
def bulk_test_data():
    """Dados em lote para testes de performance"""
    def generate_bulk_data(count=100):
        data_list = []
        for i in range(count):
            data_list.append({
                'nome_completo': f'Usuário Teste {i:03d}',
                'email': f'teste{i:03d}@email.com',
                'cpf': f'{random.randint(10000000000, 99999999999)}',
                'telefone': f'(11) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'senha': f'senha{i:03d}'
            })
        return data_list
    
    return generate_bulk_data 