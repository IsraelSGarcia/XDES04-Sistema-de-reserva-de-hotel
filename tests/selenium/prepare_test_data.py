#!/usr/bin/env python3
"""
Script para preparar dados únicos para testes Selenium
Garante que cada execução use dados diferentes e válidos
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta
import random

def get_db_path():
    """Retorna o caminho do banco de dados"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..', 'data')
    return os.path.join(project_root, 'restel.db')

def clear_test_data():
    """Remove dados de teste anteriores"""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Remover reservas de teste (incluindo novos padrões)
        cursor.execute("DELETE FROM reservas WHERE quarto_id IN (SELECT id FROM quartos WHERE numero IN ('101', '404', '5050'))")
        
        # Remover quartos de teste (incluindo novos números)
        cursor.execute("DELETE FROM quartos WHERE numero IN ('101', '404', '5050')")
        
        # Remover hóspedes de teste (incluindo email antigo)
        cursor.execute("DELETE FROM hospedes WHERE email IN ('dfvsdf@gmail.com', 'ana.costa@teste.com') OR email LIKE '%teste.com'")
        
        conn.commit()
        print("✅ Dados de teste anteriores removidos")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados: {e}")
        return False
    finally:
        conn.close()

def create_test_rooms():
    """Cria quartos únicos para os testes"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Quartos baseados no Release 01.side atualizado
    test_rooms = [
        (101, 'Standard', 2, 300.00, 'Disponível'),  # Usado nos testes de reserva
        (404, 'Luxo', 3, 600.00, 'Disponível'),      # Usado no teste de cadastro válido
        # Nota: 5050 é usado no teste inválido, então não criamos no banco
    ]
    
    try:
        for numero, tipo, capacidade, preco, status in test_rooms:
            cursor.execute("""
                INSERT OR REPLACE INTO quartos (numero, tipo, capacidade, preco_diaria, status)
                VALUES (?, ?, ?, ?, ?)
            """, (numero, tipo, capacidade, preco, status))
        
        conn.commit()
        print(f"✅ {len(test_rooms)} quartos de teste criados")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar quartos: {e}")
        return False
    finally:
        conn.close()

def create_test_guests():
    """Cria hóspedes únicos para os testes"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Hóspedes baseados no Release 01.side atualizado
    test_guests = [
        # Hóspede principal usado nos testes (email/senha do arquivo)
        ('fcgvhbjk', 'dfvsdf@gmail.com', 'fgsgfgsg', '11987654321', '12345678901'),
        # Hóspede para teste admin
        ('Ana Costa', 'ana.costa@teste.com', 'senha123', '11987654324', '12345678904'),
    ]
    
    try:
        for nome, email, senha, telefone, cpf in test_guests:
            cursor.execute("""
                INSERT OR REPLACE INTO hospedes (nome_completo, email, senha, telefone, cpf)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, email, senha, telefone, cpf))
        
        conn.commit()
        print(f"✅ {len(test_guests)} hóspedes de teste criados")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar hóspedes: {e}")
        return False
    finally:
        conn.close()

def generate_test_dates():
    """Gera datas futuras válidas para os testes"""
    today = datetime.now()
    
    # Datas baseadas no Release 01.side (sempre futuras)
    base_date = today + timedelta(days=30)  # Garantir que seja futuro
    
    dates = {
        'hospede_checkin': base_date.strftime('%Y-%m-%d'),                    # 2025-06-27 equivalente
        'hospede_checkout': (base_date + timedelta(days=1)).strftime('%Y-%m-%d'),  # 2025-06-28 equivalente
        'admin_checkin': (base_date + timedelta(days=1)).strftime('%Y-%m-%d'),     # 2025-06-28 equivalente
        'admin_checkout': (base_date + timedelta(days=2)).strftime('%Y-%m-%d'),    # 2025-06-29 equivalente
    }
    
    print("✅ Datas de teste geradas:")
    for key, date in dates.items():
        print(f"   {key}: {date}")
    
    return dates

def main():
    """Função principal"""
    print("🔧 Preparando dados para testes Selenium...")
    print("=" * 50)
    
    # Verificar se o banco existe
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        print("   Execute o sistema primeiro para criar o banco.")
        sys.exit(1)
    
    # Limpar dados anteriores
    if not clear_test_data():
        sys.exit(1)
    
    # Criar dados de teste
    if not create_test_rooms():
        sys.exit(1)
    
    if not create_test_guests():
        sys.exit(1)
    
    # Gerar datas
    dates = generate_test_dates()
    
    print("=" * 50)
    print("✅ Preparação concluída! Os testes agora usam dados únicos.")
    print("\n📋 Dados criados:")
    print("   • Quartos: 101 (Standard), 404 (Luxo)")
    print("   • Hóspedes: dfvsdf@gmail.com, ana.costa@teste.com")
    print("   • Datas: sempre futuras e válidas")
    print("\n⚠️  Nota: Quarto 5050 é usado para teste inválido (não criado no banco)")
    print("\n🚀 Execute os testes Selenium agora!")

if __name__ == "__main__":
    main() 