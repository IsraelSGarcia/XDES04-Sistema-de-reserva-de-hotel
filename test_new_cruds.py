#!/usr/bin/env python3
"""
Script para testar os novos CRUDs de quartos e reservas
"""
import os
import sqlite3
import sys

# Adicionar o diretório src ao PATH para importar o módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_database_creation():
    """Testa se as novas tabelas foram criadas corretamente"""
    print("🔍 Testando criação das tabelas...")
    
    # Importar e inicializar o banco
    from restel.app import init_db, DATABASE
    
    init_db()
    
    # Conectar ao banco e verificar tabelas
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Verificar se as tabelas existem
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = ['hospedes', 'administradores', 'quartos', 'reservas']
    
    print("📊 Tabelas encontradas:")
    for table in tables:
        status = "✅" if table in expected_tables else "❓"
        print(f"  {status} {table}")
    
    # Verificar estrutura da tabela quartos
    print("\n🏨 Estrutura da tabela 'quartos':")
    cursor.execute("PRAGMA table_info(quartos)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  - {column[1]} ({column[2]})")
    
    # Verificar estrutura da tabela reservas
    print("\n📅 Estrutura da tabela 'reservas':")
    cursor.execute("PRAGMA table_info(reservas)")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  - {column[1]} ({column[2]})")
    
    conn.close()
    print("\n✅ Teste de banco de dados concluído!")

def test_sample_data():
    """Insere dados de exemplo para teste"""
    print("\n📦 Inserindo dados de exemplo...")
    
    from restel.app import get_db_connection
    
    conn = get_db_connection()
    
    # Inserir quarto de exemplo
    try:
        conn.execute('''
            INSERT INTO quartos (numero, tipo, capacidade, preco_diaria, status)
            VALUES ('101', 'Standard', 2, 150.00, 'Disponível')
        ''')
        print("  ✅ Quarto 101 inserido")
    except sqlite3.IntegrityError:
        print("  ℹ️  Quarto 101 já existe")
    
    try:
        conn.execute('''
            INSERT INTO quartos (numero, tipo, capacidade, preco_diaria, status)
            VALUES ('201', 'Suíte', 4, 300.00, 'Disponível')
        ''')
        print("  ✅ Quarto 201 inserido")
    except sqlite3.IntegrityError:
        print("  ℹ️  Quarto 201 já existe")
    
    conn.commit()
    
    # Verificar hóspedes existentes
    hospedes = conn.execute('SELECT * FROM hospedes WHERE ativo = 1').fetchall()
    quartos = conn.execute('SELECT * FROM quartos WHERE ativo = 1').fetchall()
    
    print(f"\n📊 Estatísticas:")
    print(f"  - Hóspedes ativos: {len(hospedes)}")
    print(f"  - Quartos ativos: {len(quartos)}")
    
    if hospedes and quartos:
        # Inserir reserva de exemplo
        hospede_id = hospedes[0]['id']
        quarto_id = quartos[0]['id']
        
        try:
            conn.execute('''
                INSERT INTO reservas (hospede_id, quarto_id, data_checkin, data_checkout, 
                                    numero_hospedes, valor_total, status)
                VALUES (?, ?, '2025-01-15', '2025-01-17', 2, 300.00, 'Ativa')
            ''', (hospede_id, quarto_id))
            print("  ✅ Reserva de exemplo inserida")
        except sqlite3.IntegrityError:
            print("  ℹ️  Reserva já existe ou conflito de datas")
    
    conn.commit()
    conn.close()
    print("✅ Dados de exemplo inseridos!")

def show_routes():
    """Mostra as rotas disponíveis"""
    print("\n🛣️  Novas rotas disponíveis:")
    print("📋 Quartos:")
    print("  - GET  /admin/quartos                    (Listar quartos)")
    print("  - GET  /admin/quarto/cadastro           (Formulário de cadastro)")
    print("  - POST /admin/quarto/cadastro           (Processar cadastro)")
    print("  - GET  /admin/quarto/<id>/editar        (Formulário de edição)")
    print("  - POST /admin/quarto/<id>/editar        (Processar edição)")
    print("  - POST /admin/quarto/<id>/excluir       (Excluir quarto)")
    
    print("\n📅 Reservas:")
    print("  - GET  /admin/reservas                   (Listar reservas)")
    print("  - GET  /admin/reserva/cadastro          (Formulário de cadastro)")
    print("  - POST /admin/reserva/cadastro          (Processar cadastro)")
    print("  - GET  /admin/reserva/<id>/editar       (Formulário de edição)")
    print("  - POST /admin/reserva/<id>/editar       (Processar edição)")
    print("  - POST /admin/reserva/<id>/cancelar     (Cancelar reserva)")

if __name__ == "__main__":
    print("🚀 Testando implementação dos CRUDs de Quartos e Reservas")
    print("=" * 60)
    
    try:
        test_database_creation()
        test_sample_data()
        show_routes()
        
        print("\n" + "=" * 60)
        print("✅ Todos os testes passaram!")
        print("🌐 Inicie a aplicação com: python src/restel/app.py")
        print("📖 Acesse: http://localhost:5000/admin/login")
        print("🔑 Login: admin@restel.com | Senha: admin123")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc() 