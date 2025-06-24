from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import re
import os
import logging
import json
from pywebpush import webpush, WebPushException # type: ignore
from py_vapid import Vapid # type: ignore

app = Flask(__name__)
app.secret_key = 'restel_secret_key_2025'

# Configurações do banco de dados
DATABASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'restel.db')

# Configuração de logs
def setup_logging():
    """Configura o sistema de logs"""
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(logs_dir, 'restel.log')),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def log_operacao(operacao, usuario_id, usuario_tipo, detalhes=''):
    """Registra operações críticas no sistema"""
    logger.info(f"OPERACAO: {operacao} | USUARIO: {usuario_tipo}:{usuario_id} | DETALHES: {detalhes}")
    
    # Salvar também no banco para auditoria
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO logs_auditoria (operacao, usuario_id, usuario_tipo, detalhes, data_operacao)
            VALUES (?, ?, ?, ?, ?)
        ''', (operacao, usuario_id, usuario_tipo, detalhes, datetime.now()))
        conn.commit()
    except Exception as e:
        logger.error(f"Erro ao salvar log no banco: {e}")
    finally:
        conn.close()

def simular_envio_email(destinatario, assunto, detalhes=''):
    """Simula envio de email (para desenvolvimento)"""
    logger.info(f"EMAIL SIMULADO: Para {destinatario} | Assunto: {assunto} | Detalhes: {detalhes}")
    # Em produção, aqui seria implementado o envio real

# --- CONFIGURAÇÃO DAS NOTIFICAÇÕES PUSH ---
try:
    VAPID_PRIVATE_KEY = open('private_key.pem', "r").read().strip()
    VAPID_PUBLIC_KEY = open('public_key.pem', "r").read().strip()
    VAPID_CLAIMS = {"sub": "mailto:admin@restel.com"}
except FileNotFoundError:
    print("ERRO: Chaves VAPID (private_key.pem, public_key.pem) não encontradas.")
    VAPID_PRIVATE_KEY, VAPID_PUBLIC_KEY = None, None

def init_db():
    """Inicializa o banco de dados e o popula com dados de exemplo se estiver vazio."""
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'restel.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- CRIAÇÃO DE TABELAS ---
    # (código de criação das tabelas que já existe) ...
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospedes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            cpf TEXT UNIQUE NOT NULL,
            telefone TEXT NOT NULL,
            senha TEXT NOT NULL,
            ativo BOOLEAN DEFAULT 1,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de administradores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS administradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT NOT NULL CHECK(perfil IN ('Master', 'Padrão')),
            ativo BOOLEAN DEFAULT 1,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de quartos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quartos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            tipo TEXT NOT NULL,
            capacidade INTEGER NOT NULL,
            preco_diaria DECIMAL(10,2) NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Disponível', 'Ocupado', 'Manutenção')),
            ativo BOOLEAN DEFAULT 1,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de reservas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hospede_id INTEGER,
            quarto_id INTEGER,
            data_checkin DATE NOT NULL,
            data_checkout DATE NOT NULL,
            numero_hospedes INTEGER NOT NULL,
            valor_total REAL NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Ativa', 'Concluída', 'Cancelada')),
            data_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospede_id) REFERENCES hospedes(id),
            FOREIGN KEY (quarto_id) REFERENCES quartos(id)
        )
    ''')
    
    # Tabela de logs de auditoria
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs_auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operacao TEXT NOT NULL,
            usuario_id INTEGER,
            usuario_tipo TEXT NOT NULL CHECK(usuario_tipo IN ('hospede', 'admin', 'sistema')),
            detalhes TEXT,
            data_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de contatos/mensagens
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contatos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            assunto TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            respondido BOOLEAN DEFAULT 0,
            data_contato TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar administrador Master padrão se não existir
    cursor.execute('SELECT COUNT(*) FROM administradores WHERE perfil = "Master"')
    if cursor.fetchone()[0] == 0:
        senha_hash = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO administradores (nome_completo, email, senha, perfil)
            VALUES (?, ?, ?, ?)
        ''', ('Administrador Master', 'admin@restel.com', senha_hash, 'Master'))
    
    # Tabela para armazenar notificações internas do site
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            usuario_tipo TEXT NOT NULL CHECK(usuario_tipo IN ('hospede', 'admin')),
            mensagem TEXT NOT NULL,
            link TEXT,
            lida INTEGER NOT NULL DEFAULT 0,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela para armazenar inscrições de Push Notification
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            usuario_tipo TEXT NOT NULL,
            subscription_json TEXT NOT NULL UNIQUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # --- VERIFICA SE O BANCO JÁ FOI POPULADO ---
    cursor.execute("SELECT COUNT(id) FROM administradores")
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        print("Banco de dados vazio. Populando com dados de exemplo...")
        from datetime import date, timedelta

        # --- Administradores ---
        cursor.execute("INSERT INTO administradores (nome_completo, email, senha, perfil) VALUES (?, ?, ?, ?)",
                       ('Admin Master', 'master@restel.com', generate_password_hash('admin'), 'Master'))
        cursor.execute("INSERT INTO administradores (nome_completo, email, senha, perfil) VALUES (?, ?, ?, ?)",
                       ('Admin Padrão', 'padrao@restel.com', generate_password_hash('admin'), 'Padrão'))

        # --- Hóspedes ---
        hospedes = [
            ('Ana Silva', 'ana.silva@email.com', '11122233344', '11987654321', generate_password_hash('123456'), 1),
            ('Bruno Costa', 'bruno.costa@email.com', '22233344455', '21987654322', generate_password_hash('123456'), 1),
            ('Carla Dias', 'carla.dias@email.com', '33344455566', '31987654323', generate_password_hash('123456'), 1),
            ('Daniel Farias', 'daniel.farias@email.com', '44455566677', '41987654324', generate_password_hash('123456'), 0),
            ('Elisa Martins', 'elisa.martins@email.com', '55566677788', '51987654325', generate_password_hash('123456'), 1)
        ]
        cursor.executemany('INSERT INTO hospedes (nome_completo, email, cpf, telefone, senha, ativo) VALUES (?, ?, ?, ?, ?, ?)', hospedes)

        # --- Quartos ---
        quartos = [
            (101, 'Solteiro', 1, 150.00, 'Disponível'), (102, 'Solteiro', 1, 150.00, 'Disponível'),
            (201, 'Casal', 2, 250.00, 'Disponível'), (202, 'Casal', 2, 250.00, 'Ocupado'),
            (301, 'Suíte Luxo', 2, 450.00, 'Disponível'), (302, 'Suíte Família', 4, 550.00, 'Manutenção')
        ]
        cursor.executemany('INSERT INTO quartos (numero, tipo, capacidade, preco_diaria, status) VALUES (?, ?, ?, ?, ?)', quartos)
        
        # Marcar quarto 202 como ocupado por uma reserva
        cursor.execute("UPDATE quartos SET status = 'Ocupado' WHERE numero = 202")


        # --- Reservas ---
        hoje = date.today()
        reservas = [
            # Reserva futura, permanece Ativa
            (1, 1, (hoje + timedelta(days=10)).isoformat(), (hoje + timedelta(days=15)).isoformat(), 1, 750.00, 'Ativa'),
            # Reserva que estaria em andamento (check-in feito), permanece Ativa
            (2, 4, (hoje - timedelta(days=2)).isoformat(), (hoje + timedelta(days=3)).isoformat(), 2, 1250.00, 'Ativa'),
            # Reserva passada (check-out feito), agora é Concluída
            (3, 3, (hoje - timedelta(days=20)).isoformat(), (hoje - timedelta(days=15)).isoformat(), 2, 1250.00, 'Concluída'),
            # Reserva futura cancelada
            (5, 5, (hoje + timedelta(days=5)).isoformat(), (hoje + timedelta(days=8)).isoformat(), 2, 1350.00, 'Cancelada'),
            # Outra reserva futura
            (1, 3, (hoje + timedelta(days=30)).isoformat(), (hoje + timedelta(days=35)).isoformat(), 2, 1250.00, 'Ativa')
        ]
        cursor.executemany('INSERT INTO reservas (hospede_id, quarto_id, data_checkin, data_checkout, numero_hospedes, valor_total, status) VALUES (?, ?, ?, ?, ?, ?, ?)', reservas)

        print("Dados de exemplo inseridos com sucesso.")

    conn.commit()
    conn.close()

def get_db_connection():
    """Retorna uma conexão com o banco de dados"""
    from flask import current_app
    # Use a database path from app config if available (for testing), else global
    db_path = current_app.config.get('DATABASE', DATABASE)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def validar_cpf(cpf):
    """Valida formato do CPF"""
    cpf = re.sub('[^0-9]', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()

def validar_email(email):
    """Valida formato do email"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

# ========== ROTAS PARA HÓSPEDES ==========

@app.route('/hospede/cadastro')
def cadastro_hospede():
    """Formulário de cadastro de hóspede"""
    return render_template('hospede_cadastro.html')

@app.route('/hospede/cadastro', methods=['POST'])
def processar_cadastro_hospede():
    """Processa o cadastro de novo hóspede"""
    # --- BEGIN TEMP DEBUG ---
    try:
        # Ensure the debug file is written to a known, accessible location,
        # e.g., the project root or a dedicated 'logs' folder.
        # For simplicity, writing to the same directory as app.py for now.
        debug_file_path = os.path.join(os.path.dirname(__file__), "processar_cadastro_hospede_debug.txt")
        with open(debug_file_path, "a") as f:
            f.write(f"--- HIT at {datetime.now()} ---\n")
            f.write(f"DATABASE path: {DATABASE}\n")
            f.write(f"Request form: {dict(request.form)}\n")
            f.write(f"Request Content-Type: {request.content_type}\n")
    except Exception as e_debug_file:
        # This print should definitely appear if file writing fails
        print(f"CRITICAL DEBUG: Error writing debug file: {e_debug_file}", flush=True)
    # --- END TEMP DEBUG ---

    # Debug: print form data
    print("Form data received:", dict(request.form), flush=True)
    print("Content-Type:", request.content_type, flush=True)
    
    # Safely get form data with error handling
    nome_completo = request.form.get('nome_completo', '').strip()
    email = request.form.get('email', '').strip().lower()
    cpf = re.sub('[^0-9]', '', request.form.get('cpf', ''))
    telefone = request.form.get('telefone', '').strip()
    senha = request.form.get('senha', '')
    
    # Validações
    if not nome_completo or not email or not cpf or not telefone or not senha:
        print("VALIDATION FAIL: Campos obrigatórios em branco.", flush=True)
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('cadastro_hospede'))
    
    if not validar_email(email):
        print(f"VALIDATION FAIL: Email inválido - '{email}'", flush=True)
        flash('Email inválido!', 'error')
        return redirect(url_for('cadastro_hospede'))
    
    if not validar_cpf(cpf):
        print(f"VALIDATION FAIL: CPF inválido - '{cpf}'", flush=True)
        flash('CPF inválido!', 'error')
        return redirect(url_for('cadastro_hospede'))
    
    if len(senha) < 6:
        print(f"VALIDATION FAIL: Senha curta - '{senha}'", flush=True)
        flash('Senha deve ter pelo menos 6 caracteres!', 'error')
        return redirect(url_for('cadastro_hospede'))
    
    conn = get_db_connection()
    
    # Verificar se email já existe
    if conn.execute('SELECT id FROM hospedes WHERE email = ?', (email,)).fetchone():
        print(f"VALIDATION FAIL: Email já cadastrado - '{email}'", flush=True)
        flash('Email já cadastrado!', 'error')
        conn.close()
        return redirect(url_for('cadastro_hospede'))
    
    # Verificar se CPF já existe
    if conn.execute('SELECT id FROM hospedes WHERE cpf = ?', (cpf,)).fetchone():
        print(f"VALIDATION FAIL: CPF já cadastrado - '{cpf}'", flush=True)
        flash('CPF já cadastrado!', 'error')
        conn.close()
        return redirect(url_for('cadastro_hospede'))
    
    # Cadastrar hóspede
    senha_hash = generate_password_hash(senha)
    cursor = conn.execute('''
        INSERT INTO hospedes (nome_completo, email, cpf, telefone, senha)
        VALUES (?, ?, ?, ?, ?)
    ''', (nome_completo, email, cpf, telefone, senha_hash))
    
    hospede_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Log da operação
    log_operacao('CADASTRO_HOSPEDE', hospede_id, 'hospede', f'Email: {email}')
    
    flash('Cadastro realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/hospede/login')
def login_hospede():
    """Formulário de login de hóspede"""
    return render_template('hospede_login.html')

@app.route('/hospede/login', methods=['POST'])
def processar_login_hospede():
    """Processa o login de hóspede"""
    email = request.form['email'].strip().lower()
    senha = request.form['senha']
    
    # Validações básicas
    if not email or not senha:
        flash('Email e senha são obrigatórios!', 'error')
        return redirect(url_for('login_hospede'))
    
    conn = get_db_connection()
    hospede = conn.execute('SELECT * FROM hospedes WHERE email = ? AND ativo = 1', (email,)).fetchone()
    conn.close()
    
    if hospede and check_password_hash(hospede['senha'], senha):
        # Login bem-sucedido
        session['hospede_id'] = hospede['id']
        session['hospede_nome'] = hospede['nome_completo']
        flash(f'Bem-vindo(a), {hospede["nome_completo"]}!', 'success')
        return redirect(url_for('painel_hospede'))
    else:
        flash('Email ou senha incorretos!', 'error')
        return redirect(url_for('login_hospede'))

@app.route('/hospede/logout')
def logout_hospede():
    """Logout de hóspede"""
    if 'hospede_id' in session:
        del session['hospede_id']
        del session['hospede_nome']
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/hospede/painel')
def painel_hospede():
    """Painel do hóspede"""
    if 'hospede_id' not in session:
        flash('Acesso negado! Faça login como hóspede.', 'error')
        return redirect(url_for('login_hospede'))
    
    conn = get_db_connection()
    
    # Estatísticas das reservas do hóspede
    hospede_id = session['hospede_id']
    reservas_ativas = conn.execute('SELECT COUNT(*) FROM reservas WHERE hospede_id = ? AND status = "Ativa"', (hospede_id,)).fetchone()[0]
    reservas_concluidas = conn.execute('SELECT COUNT(*) FROM reservas WHERE hospede_id = ? AND status = "Concluída"', (hospede_id,)).fetchone()[0]
    reservas_canceladas = conn.execute('SELECT COUNT(*) FROM reservas WHERE hospede_id = ? AND status = "Cancelada"', (hospede_id,)).fetchone()[0]
    
    # Próximas reservas
    proximas_reservas = conn.execute('''
        SELECT r.*, q.numero as quarto_numero, q.tipo as quarto_tipo
        FROM reservas r
        JOIN quartos q ON r.quarto_id = q.id
        WHERE r.hospede_id = ? AND r.status = 'Ativa' AND r.data_checkin >= ?
        ORDER BY r.data_checkin ASC
        LIMIT 3
    ''', (hospede_id, datetime.now().strftime('%Y-%m-%d'))).fetchall()
    
    conn.close()
    
    return render_template('hospede_painel.html',
                         reservas_ativas=reservas_ativas,
                         reservas_concluidas=reservas_concluidas,
                         reservas_canceladas=reservas_canceladas,
                         proximas_reservas=proximas_reservas)

@app.route('/hospede/reserva/nova')
def nova_reserva_hospede():
    """Formulário para hóspede fazer nova reserva"""
    if 'hospede_id' not in session:
        flash('Acesso negado! Faça login para fazer uma reserva.', 'error')
        return redirect(url_for('login_hospede'))
    
    conn = get_db_connection()
    quartos = conn.execute('SELECT * FROM quartos WHERE ativo = 1 AND status = "Disponível" ORDER BY numero').fetchall()
    conn.close()
    
    return render_template('hospede_reserva_nova.html', quartos=quartos)

@app.route('/api/disponibilidade/<int:quarto_id>')
def api_disponibilidade_quarto(quarto_id):
    """Retorna um JSON com as datas em que um quarto está indisponível."""
    conn = get_db_connection()
    # Apenas reservas 'Ativa' bloqueiam datas futuras.
    reservas = conn.execute('''
        SELECT data_checkin, data_checkout 
        FROM reservas 
        WHERE quarto_id = ? AND status = 'Ativa'
        ORDER BY data_checkin
    ''', (quarto_id,)).fetchall()
    conn.close()
    
    # Converter para formato JSON
    periodos_ocupados = []
    for reserva in reservas:
        periodos_ocupados.append({
            'start': reserva['data_checkin'],
            'end': reserva['data_checkout']
        })
    
    return {'periodos_ocupados': periodos_ocupados}

@app.route('/hospede/reserva/nova', methods=['POST'])
def processar_nova_reserva_hospede():
    """Processa a nova reserva feita pelo hóspede"""
    if 'hospede_id' not in session:
        flash('Você precisa estar logado para fazer uma reserva.', 'error')
        return redirect(url_for('login_hospede'))

    hospede_id = session['hospede_id']
    quarto_id = request.form.get('quarto_id', type=int)
    data_checkin_str = request.form.get('data_checkin')
    data_checkout_str = request.form.get('data_checkout')
    numero_hospedes = request.form.get('numero_hospedes', type=int)

    if not all([quarto_id, data_checkin_str, data_checkout_str, numero_hospedes]):
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('nova_reserva_hospede'))

    # Checagem para satisfazer o linter, embora 'all' já verifique
    if data_checkin_str is None or data_checkout_str is None:
        flash('Datas de check-in e check-out são obrigatórias.', 'error')
        return redirect(url_for('nova_reserva_hospede'))

    try:
        data_checkin = datetime.strptime(data_checkin_str, '%Y-%m-%d').date()
        data_checkout = datetime.strptime(data_checkout_str, '%Y-%m-%d').date()
    except ValueError:
        flash('Formato de data inválido!', 'error')
        return redirect(url_for('nova_reserva_hospede'))

    if data_checkin >= data_checkout:
        flash('A data de check-out deve ser posterior à data de check-in.', 'error')
        return redirect(url_for('nova_reserva_hospede'))

    conn = get_db_connection()
    quarto = conn.execute('SELECT * FROM quartos WHERE id = ?', (quarto_id,)).fetchone()

    if not quarto:
        flash('Quarto inválido!', 'error')
        conn.close()
        return redirect(url_for('nova_reserva_hospede'))

    if numero_hospedes > quarto['capacidade']:
        flash('O número de hóspedes excede a capacidade do quarto.', 'error')
        conn.close()
        return redirect(url_for('nova_reserva_hospede'))
        
    # [CORREÇÃO] A lógica de verificação de conflitos estava incorreta
    # Agora só precisa verificar status 'Ativa', pois 'Check-in' não existe mais como status de reserva.
    reservas_conflitantes = conn.execute('''
        SELECT id FROM reservas
        WHERE quarto_id = ? AND status = 'Ativa'
              AND (
                  (data_checkin < ? AND data_checkout > ?)
              )
    ''', (quarto_id, data_checkout_str, data_checkin_str)).fetchall()

    if reservas_conflitantes:
        flash('O quarto não está disponível para as datas selecionadas.', 'error')
        conn.close()
        return redirect(url_for('nova_reserva_hospede'))

    # Cálculo do valor
    duracao_estadia = (data_checkout - data_checkin).days
    valor_total = duracao_estadia * quarto['preco_diaria']

    # Inserir reserva
    cursor = conn.execute('''
        INSERT INTO reservas (hospede_id, quarto_id, data_checkin, data_checkout, numero_hospedes, valor_total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (hospede_id, quarto_id, data_checkin_str, data_checkout_str, numero_hospedes, valor_total, 'Ativa'))
    
    reserva_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_operacao('CADASTRO_RESERVA', hospede_id, 'hospede', f'Reserva ID: {reserva_id}')

    # Notificação
    criar_notificacao(hospede_id, 'hospede', 
                      f"Sua reserva #{reserva_id} foi realizada com sucesso!", 
                      url_for('minhas_reservas_hospede'))

    flash('Reserva realizada com sucesso!', 'success')
    return redirect(url_for('minhas_reservas_hospede'))

@app.route('/hospede/reservas')
def minhas_reservas_hospede():
    """Lista reservas do hóspede"""
    if 'hospede_id' not in session:
        flash('Acesso negado! Faça login para ver suas reservas.', 'error')
        return redirect(url_for('login_hospede'))
    
    hospede_id = session['hospede_id']
    conn = get_db_connection()
    
    # Buscar todas as reservas do hóspede
    reservas_raw = conn.execute('''
        SELECT r.*, q.numero as quarto_numero, q.tipo as quarto_tipo
        FROM reservas r
        JOIN quartos q ON r.quarto_id = q.id
        WHERE r.hospede_id = ?
        ORDER BY r.data_checkin DESC
    ''', (hospede_id,)).fetchall()
    
    conn.close()
    
    # Adicionar informações sobre possibilidade de edição/cancelamento
    hoje = datetime.now().date()
    
    reservas = []
    for reserva in reservas_raw:
        reserva_dict = dict(reserva)
        checkin_date = datetime.strptime(reserva['data_checkin'], '%Y-%m-%d').date()
        dias_para_checkin = (checkin_date - hoje).days
        
        # RF17: Edição permitida com mais de 24h de antecedência (> 1 dia)
        reserva_dict['pode_editar'] = (
            reserva['status'] == 'Ativa' and dias_para_checkin > 1
        )
        
        # RF16: Cancelamento permitido com pelo menos 24h de antecedência (>= 1 dia)
        reserva_dict['pode_cancelar'] = (
            reserva['status'] == 'Ativa' and dias_para_checkin >= 1
        )
        
        reservas.append(reserva_dict)
    
    return render_template('hospede_reservas.html', reservas=reservas)

@app.route('/hospede/reserva/<int:reserva_id>/editar')
def editar_reserva_hospede(reserva_id):
    """Formulário para hóspede editar sua reserva"""
    if 'hospede_id' not in session:
        flash('Acesso negado! Faça login para editar reservas.', 'error')
        return redirect(url_for('login_hospede'))
    
    hospede_id = session['hospede_id']
    conn = get_db_connection()
    
    # Buscar reserva do hóspede
    reserva = conn.execute('''
        SELECT r.*, q.numero as quarto_numero, q.tipo as quarto_tipo, q.capacidade, q.preco_diaria
        FROM reservas r
        JOIN quartos q ON r.quarto_id = q.id
        WHERE r.id = ? AND r.hospede_id = ?
    ''', (reserva_id, hospede_id)).fetchone()
    
    if not reserva:
        flash('Reserva não encontrada!', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))
    
    # Verificar regra de 24h
    checkin_date = datetime.strptime(reserva['data_checkin'], '%Y-%m-%d').date()
    hoje = datetime.now().date()
    limite_edicao = checkin_date - timedelta(days=1)
    
    if hoje >= limite_edicao and reserva['status'] == 'Ativa':
        flash('Não é possível editar a reserva. Faltam menos de 24 horas para o check-in!', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))
    
    if reserva['status'] not in ['Ativa']:
        flash('Apenas reservas ativas podem ser editadas.', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))
    
    conn.close()
    return render_template('hospede_reserva_editar.html', reserva=reserva)

@app.route('/hospede/reserva/<int:reserva_id>/editar', methods=['POST'])
def processar_edicao_reserva_hospede(reserva_id):
    """Processa edição de reserva pelo hóspede"""
    if 'hospede_id' not in session:
        flash('Acesso negado! Faça login para editar reservas.', 'error')
        return redirect(url_for('login_hospede'))
    
    hospede_id = session['hospede_id']
    data_checkin = request.form['data_checkin']
    data_checkout = request.form['data_checkout']
    numero_hospedes = request.form['numero_hospedes']
    
    # Validações
    if not data_checkin or not data_checkout or not numero_hospedes:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('editar_reserva_hospede', reserva_id=reserva_id))
    
    try:
        from datetime import datetime, timedelta
        checkin = datetime.strptime(data_checkin, '%Y-%m-%d').date()
        checkout = datetime.strptime(data_checkout, '%Y-%m-%d').date()
        numero_hospedes = int(numero_hospedes)
    except ValueError:
        flash('Datas ou número de hóspedes inválidos!', 'error')
        return redirect(url_for('editar_reserva_hospede', reserva_id=reserva_id))
    
    if checkin >= checkout:
        flash('Data de check-out deve ser posterior ao check-in!', 'error')
        return redirect(url_for('editar_reserva_hospede', reserva_id=reserva_id))
    
    # Verificar regra de 24h
    hoje = datetime.now().date()
    limite_edicao = checkin - timedelta(days=1)
    
    if hoje >= limite_edicao:
        flash('Não é possível editar a reserva. Faltam menos de 24 horas para o check-in!', 'error')
        return redirect(url_for('editar_reserva_hospede', reserva_id=reserva_id))
    
    if numero_hospedes <= 0:
        flash('Número de hóspedes deve ser positivo!', 'error')
        return redirect(url_for('editar_reserva_hospede', reserva_id=reserva_id))
    
    conn = get_db_connection()
    
    # Obter dados da reserva atual
    reserva_atual = conn.execute('SELECT * FROM reservas WHERE id = ? AND hospede_id = ?', (reserva_id, hospede_id)).fetchone()
    if not reserva_atual:
        flash('Reserva não encontrada!', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))
    
    # Verificar capacidade do quarto
    quarto = conn.execute('SELECT * FROM quartos WHERE id = ?', (reserva_atual['quarto_id'],)).fetchone()
    if numero_hospedes > quarto['capacidade']:
        flash('Número de hóspedes excede a capacidade do quarto!', 'error')
        conn.close()
        return redirect(url_for('editar_reserva_hospede', reserva_id=reserva_id))
    
    # Verificar conflitos de reserva (excluindo a reserva atual)
    conflitos = conn.execute('''
        SELECT COUNT(*) FROM reservas 
        WHERE quarto_id = ? AND status = 'Ativa' AND id != ?
        AND NOT (data_checkout <= ? OR data_checkin >= ?)
    ''', (reserva_atual['quarto_id'], reserva_id, data_checkin, data_checkout)).fetchone()[0]
    
    if conflitos > 0:
        flash('Já existe uma reserva para este quarto no período selecionado!', 'error')
        conn.close()
        return redirect(url_for('editar_reserva_hospede', reserva_id=reserva_id))
    
    # Recalcular valor total
    dias = (checkout - checkin).days
    valor_total = dias * float(quarto['preco_diaria'])
    
    # Atualizar dados da reserva
    conn.execute('''
        UPDATE reservas 
        SET data_checkin = ?, data_checkout = ?, numero_hospedes = ?, valor_total = ?
        WHERE id = ? AND hospede_id = ?
    ''', (data_checkin, data_checkout, numero_hospedes, valor_total, reserva_id, hospede_id))
    
    conn.commit()
    conn.close()
    
    flash('Reserva atualizada com sucesso!', 'success')
    return redirect(url_for('minhas_reservas_hospede'))

@app.route('/hospede/reserva/<int:reserva_id>/cancelar', methods=['POST'])
def cancelar_reserva_hospede(reserva_id):
    """Processa o cancelamento de uma reserva pelo hóspede"""
    if 'hospede_id' not in session:
        return redirect(url_for('login_hospede'))

    conn = get_db_connection()
    reserva = conn.execute('SELECT * FROM reservas WHERE id = ? AND hospede_id = ?',
                           (reserva_id, session['hospede_id'])).fetchone()

    if not reserva:
        flash('Reserva não encontrada ou não pertence a você.', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))

    hoje_date = datetime.now().date()
    checkin_date = datetime.strptime(reserva['data_checkin'], '%Y-%m-%d').date()

    # RF16 - Não pode cancelar com menos de 24h de antecedência
    if (checkin_date - hoje_date).days < 1 and reserva['status'] == 'Ativa':
        flash('Não é possível cancelar uma reserva com menos de 24 horas de antecedência do check-in.', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))

    # Só pode cancelar reservas ativas
    if reserva['status'] not in ['Ativa']:
        flash('Apenas reservas ativas podem ser canceladas.', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))
        
    conn.execute('UPDATE reservas SET status = ? WHERE id = ?', ('Cancelada', reserva_id))
    conn.commit()

    log_operacao('CANCELAMENTO_RESERVA', session['hospede_id'], 'hospede', f'Reserva ID: {reserva_id}')

    criar_notificacao(session['hospede_id'], 'hospede',
                      f'Sua reserva #{reserva_id} foi cancelada.',
                      url_for('minhas_reservas_hospede'))
    
    conn.close()
    flash('Reserva cancelada com sucesso!', 'success')
    return redirect(url_for('minhas_reservas_hospede'))

# ========== ROTAS PARA ADMINISTRADORES ==========

@app.route('/admin/login')
def login_admin():
    """Página de login do administrador"""
    return render_template('admin_login.html')

@app.route('/admin/login', methods=['POST'])
def processar_login_admin():
    """Processa o login do administrador"""
    email = request.form['email'].strip().lower()
    senha = request.form['senha']
    
    conn = get_db_connection()
    admin = conn.execute('''
        SELECT * FROM administradores 
        WHERE email = ? AND ativo = 1
    ''', (email,)).fetchone()
    conn.close()
    
    if admin and check_password_hash(admin['senha'], senha):
        session['admin_id'] = admin['id']
        session['admin_nome'] = admin['nome_completo']
        session['admin_perfil'] = admin['perfil']
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('painel_admin'))
    else:
        flash('Email ou senha incorretos!', 'error')
        return redirect(url_for('login_admin'))

@app.route('/admin/logout')
def logout_admin():
    """Logout do administrador"""
    from flask import make_response
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    response = make_response(redirect(url_for('index')))
    response.set_cookie('session', '', expires=0)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/admin/painel')
def painel_admin():
    """Painel administrativo"""
    print(f"Session data in painel_admin: {dict(session)}")  # Debug session
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    # Buscar estatísticas para o painel
    conn = get_db_connection()
    
    # Total de hóspedes ativos
    total_hospedes = conn.execute('SELECT COUNT(*) FROM hospedes WHERE ativo = 1').fetchone()[0]
    
    # Total de quartos
    total_quartos = conn.execute('SELECT COUNT(*) FROM quartos').fetchone()[0]
    
    # Total de reservas ativas
    total_reservas_ativas = conn.execute(
        'SELECT COUNT(*) FROM reservas WHERE status = "Ativa"'
    ).fetchone()[0]
    
    # Check-ins previstos para hoje
    hoje = datetime.now().strftime('%Y-%m-%d')
    checkins_hoje = conn.execute(
        'SELECT COUNT(*) FROM reservas WHERE data_checkin = ? AND status = "Ativa"', (hoje,)
    ).fetchone()[0]
    
    conn.close()
    
    return render_template('admin_painel.html',
                         total_hospedes=total_hospedes,
                         total_quartos=total_quartos,
                         total_reservas_ativas=total_reservas_ativas,
                         checkins_hoje=checkins_hoje)

@app.route('/admin/hospedes')
def gerenciar_hospedes():
    """Lista e gerencia hóspedes"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    filtro_nome = request.args.get('nome', '')
    filtro_cpf = request.args.get('cpf', '')
    filtro_email = request.args.get('email', '')
    filtro_status = request.args.get('status', '')
    
    query = 'SELECT * FROM hospedes WHERE 1=1'
    params = []
    
    if filtro_nome:
        query += ' AND nome_completo LIKE ?'
        params.append(f'%{filtro_nome}%')
    
    if filtro_cpf:
        cpf_limpo = re.sub('[^0-9]', '', filtro_cpf)
        query += ' AND cpf LIKE ?'
        params.append(f'%{cpf_limpo}%')
    
    if filtro_email:
        query += ' AND email LIKE ?'
        params.append(f'%{filtro_email}%')
    
    if filtro_status:
        if filtro_status == 'ativo':
            query += ' AND ativo = 1'
        elif filtro_status == 'inativo':
            query += ' AND ativo = 0'
    
    query += ' ORDER BY data_cadastro DESC'
    
    hospedes = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('admin_hospedes.html', hospedes=hospedes,
                         filtro_nome=filtro_nome, filtro_cpf=filtro_cpf,
                         filtro_email=filtro_email, filtro_status=filtro_status)

@app.route('/admin/hospede/<int:hospede_id>/editar')
def editar_hospede(hospede_id):
    """Formulário para editar hóspede"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    hospede = conn.execute('SELECT * FROM hospedes WHERE id = ?', (hospede_id,)).fetchone()
    conn.close()
    
    if not hospede:
        flash('Hóspede não encontrado!', 'error')
        return redirect(url_for('gerenciar_hospedes'))
    
    return render_template('admin_hospede_editar.html', hospede=hospede)

@app.route('/admin/hospede/<int:hospede_id>/editar', methods=['POST'])
def processar_edicao_hospede(hospede_id):
    """Processa a edição dos dados do hóspede"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    nome_completo = request.form['nome_completo'].strip()
    email = request.form['email'].strip().lower()
    telefone = request.form['telefone'].strip()
    
    # Validações
    if not nome_completo or not email or not telefone:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('editar_hospede', hospede_id=hospede_id))
    
    if not validar_email(email):
        flash('Email inválido!', 'error')
        return redirect(url_for('editar_hospede', hospede_id=hospede_id))
    
    conn = get_db_connection()
    
    # Verificar se email já existe (exceto para o próprio hóspede)
    existing = conn.execute('SELECT id FROM hospedes WHERE email = ? AND id != ?', (email, hospede_id)).fetchone()
    if existing:
        flash('Email já está sendo usado por outro hóspede!', 'error')
        conn.close()
        return redirect(url_for('editar_hospede', hospede_id=hospede_id))
    
    # Atualizar dados
    conn.execute('''
        UPDATE hospedes 
        SET nome_completo = ?, email = ?, telefone = ?
        WHERE id = ?
    ''', (nome_completo, email, telefone, hospede_id))
    
    conn.commit()
    conn.close()
    
    flash('Dados do hóspede atualizados com sucesso!', 'success')
    return redirect(url_for('gerenciar_hospedes'))

@app.route('/admin/hospede/<int:hospede_id>/excluir', methods=['POST'])
def excluir_hospede(hospede_id):
    """Exclui (inativa) um hóspede"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    
    # Exclusão lógica - marca como inativo
    conn.execute('UPDATE hospedes SET ativo = 0 WHERE id = ?', (hospede_id,))
    conn.commit()
    conn.close()
    
    flash('Hóspede excluído com sucesso!', 'success')
    return redirect(url_for('gerenciar_hospedes'))

@app.route('/admin/administradores')
def gerenciar_administradores():
    """Lista e gerencia administradores (apenas para Master)"""
    if 'admin_id' not in session or session.get('admin_perfil') != 'Master':
        flash('Acesso negado! Apenas administradores Master podem acessar esta área.', 'error')
        return redirect(url_for('painel_admin'))
    
    conn = get_db_connection()
    administradores = conn.execute('SELECT * FROM administradores ORDER BY data_cadastro DESC').fetchall()
    conn.close()
    
    return render_template('admin_administradores.html', administradores=administradores)

@app.route('/admin/administrador/cadastro')
def cadastro_administrador():
    """Formulário de cadastro de administrador (apenas para Master)"""
    if 'admin_id' not in session or session.get('admin_perfil') != 'Master':
        flash('Acesso negado! Apenas administradores Master podem cadastrar novos administradores.', 'error')
        return redirect(url_for('painel_admin'))
    
    return render_template('admin_administrador_cadastro.html')

@app.route('/admin/administrador/cadastro', methods=['POST'])
def processar_cadastro_administrador():
    """Processa o cadastro de novo administrador"""
    if 'admin_id' not in session or session.get('admin_perfil') != 'Master':
        flash('Acesso negado! Apenas administradores Master podem cadastrar novos administradores.', 'error')
        return redirect(url_for('painel_admin'))
    
    nome_completo = request.form['nome_completo'].strip()
    email = request.form['email'].strip().lower()
    senha = request.form['senha']
    perfil = request.form['perfil']
    
    # Validações
    if not nome_completo or not email or not senha or not perfil:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('cadastro_administrador'))
    
    if not validar_email(email):
        flash('Email inválido!', 'error')
        return redirect(url_for('cadastro_administrador'))
    
    if len(senha) < 6:
        flash('Senha deve ter pelo menos 6 caracteres!', 'error')
        return redirect(url_for('cadastro_administrador'))
    
    if perfil not in ['Master', 'Padrão']:
        flash('Perfil inválido!', 'error')
        return redirect(url_for('cadastro_administrador'))
    
    conn = get_db_connection()
    
    # Verificar se email já existe
    if conn.execute('SELECT id FROM administradores WHERE email = ?', (email,)).fetchone():
        flash('Email já cadastrado!', 'error')
        conn.close()
        return redirect(url_for('cadastro_administrador'))
    
    # Cadastrar administrador
    senha_hash = generate_password_hash(senha)
    conn.execute('''
        INSERT INTO administradores (nome_completo, email, senha, perfil)
        VALUES (?, ?, ?, ?)
    ''', (nome_completo, email, senha_hash, perfil))
    
    conn.commit()
    conn.close()
    
    flash('Administrador cadastrado com sucesso!', 'success')
    return redirect(url_for('gerenciar_administradores'))

@app.route('/admin/administrador/<int:admin_id>/editar')
def editar_administrador(admin_id):
    """Formulário para editar administrador (apenas para Master)"""
    if 'admin_id' not in session or session.get('admin_perfil') != 'Master':
        flash('Acesso negado! Apenas administradores Master podem editar administradores.', 'error')
        return redirect(url_for('painel_admin'))
    
    conn = get_db_connection()
    administrador = conn.execute('SELECT * FROM administradores WHERE id = ?', (admin_id,)).fetchone()
    conn.close()
    
    if not administrador:
        flash('Administrador não encontrado!', 'error')
        return redirect(url_for('gerenciar_administradores'))
    
    return render_template('admin_administrador_editar.html', administrador=administrador)

@app.route('/admin/administrador/<int:admin_id>/editar', methods=['POST'])
def processar_edicao_administrador(admin_id):
    """Processa a edição dos dados do administrador"""
    if 'admin_id' not in session or session.get('admin_perfil') != 'Master':
        flash('Acesso negado! Apenas administradores Master podem editar administradores.', 'error')
        return redirect(url_for('painel_admin'))
    
    nome_completo = request.form['nome_completo'].strip()
    email = request.form['email'].strip().lower()
    perfil = request.form['perfil']
    
    # Validações
    if not nome_completo or not email or not perfil:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('editar_administrador', admin_id=admin_id))
    
    if not validar_email(email):
        flash('Email inválido!', 'error')
        return redirect(url_for('editar_administrador', admin_id=admin_id))
    
    if perfil not in ['Master', 'Padrão']:
        flash('Perfil inválido!', 'error')
        return redirect(url_for('editar_administrador', admin_id=admin_id))
    
    conn = get_db_connection()
    
    # Verificar se email já existe (exceto para o próprio administrador)
    existing = conn.execute('SELECT id FROM administradores WHERE email = ? AND id != ?', (email, admin_id)).fetchone()
    if existing:
        flash('Email já está sendo usado por outro administrador!', 'error')
        conn.close()
        return redirect(url_for('editar_administrador', admin_id=admin_id))
    
    # Atualizar dados
    conn.execute('''
        UPDATE administradores 
        SET nome_completo = ?, email = ?, perfil = ?
        WHERE id = ?
    ''', (nome_completo, email, perfil, admin_id))
    
    conn.commit()
    conn.close()
    
    flash('Dados do administrador atualizados com sucesso!', 'success')
    return redirect(url_for('gerenciar_administradores'))

@app.route('/admin/administrador/<int:admin_id>/excluir', methods=['POST'])
def excluir_administrador(admin_id):
    """Exclui (inativa) um administrador"""
    if 'admin_id' not in session or session.get('admin_perfil') != 'Master':
        flash('Acesso negado! Apenas administradores Master podem excluir administradores.', 'error')
        return redirect(url_for('painel_admin'))
    
    # Não permitir auto-exclusão
    if admin_id == session.get('admin_id'):
        flash('Você não pode excluir sua própria conta!', 'error')
        return redirect(url_for('gerenciar_administradores'))
    
    conn = get_db_connection()
    
    # Exclusão lógica - marca como inativo
    conn.execute('UPDATE administradores SET ativo = 0 WHERE id = ?', (admin_id,))
    conn.commit()
    conn.close()
    
    flash('Administrador excluído com sucesso!', 'success')
    return redirect(url_for('gerenciar_administradores'))

# ========== ROTAS PARA QUARTOS ==========

@app.route('/admin/quartos')
def gerenciar_quartos():
    """Lista e gerencia quartos"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    # Parâmetros de busca
    busca_numero = request.args.get('numero', '').strip()
    busca_tipo = request.args.get('tipo', '').strip()
    busca_status = request.args.get('status', '').strip()
    busca_capacidade = request.args.get('capacidade', '').strip()
    
    conn = get_db_connection()
    
    # Query base
    query = '''
        SELECT * FROM quartos 
        WHERE ativo = 1
    '''
    params = []
    
    # Adicionar filtros se informados
    if busca_numero:
        query += ' AND numero LIKE ?'
        params.append(f'%{busca_numero}%')
    
    if busca_tipo:
        query += ' AND tipo LIKE ?'
        params.append(f'%{busca_tipo}%')
    
    if busca_status:
        query += ' AND status = ?'
        params.append(busca_status)
    
    if busca_capacidade:
        try:
            capacidade_num = int(busca_capacidade)
            query += ' AND capacidade >= ?'
            params.append(capacidade_num)
        except ValueError:
            pass  # Ignorar se não for um número válido
    
    query += ' ORDER BY numero'
    
    quartos = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('admin_quartos.html', 
                         quartos=quartos,
                         busca_numero=busca_numero,
                         busca_tipo=busca_tipo,
                         busca_status=busca_status,
                         busca_capacidade=busca_capacidade)

@app.route('/admin/quarto/cadastro')
def cadastro_quarto():
    """Formulário de cadastro de quarto"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    return render_template('admin_quarto_cadastro.html')

@app.route('/admin/quarto/cadastro', methods=['POST'])
def processar_cadastro_quarto():
    """Processa o cadastro de novo quarto"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    numero = request.form['numero'].strip()
    tipo = request.form['tipo'].strip()
    capacidade = request.form['capacidade']
    preco_diaria = request.form['preco_diaria']
    status = request.form['status']
    
    # Validações
    if not numero or not tipo or not capacidade or not preco_diaria or not status:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('cadastro_quarto'))
    
    try:
        capacidade = int(capacidade)
        preco_diaria = float(preco_diaria)
    except ValueError:
        flash('Capacidade deve ser um número inteiro e preço deve ser um valor decimal válido!', 'error')
        return redirect(url_for('cadastro_quarto'))
    
    if capacidade <= 0 or preco_diaria <= 0:
        flash('Capacidade e preço devem ser valores positivos!', 'error')
        return redirect(url_for('cadastro_quarto'))
    
    if status not in ['Disponível', 'Ocupado', 'Manutenção']:
        flash('Status inválido!', 'error')
        return redirect(url_for('cadastro_quarto'))
    
    conn = get_db_connection()
    
    # Verificar se número já existe
    if conn.execute('SELECT id FROM quartos WHERE numero = ?', (numero,)).fetchone():
        flash('Número de quarto já cadastrado!', 'error')
        conn.close()
        return redirect(url_for('cadastro_quarto'))
    
    # Cadastrar quarto
    conn.execute('''
        INSERT INTO quartos (numero, tipo, capacidade, preco_diaria, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (numero, tipo, capacidade, preco_diaria, status))
    
    conn.commit()
    conn.close()
    
    flash('Quarto cadastrado com sucesso!', 'success')
    return redirect(url_for('gerenciar_quartos'))

@app.route('/admin/quarto/<int:quarto_id>/editar')
def editar_quarto(quarto_id):
    """Formulário para editar quarto"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    quarto = conn.execute('SELECT * FROM quartos WHERE id = ? AND ativo = 1', (quarto_id,)).fetchone()
    conn.close()
    
    if not quarto:
        flash('Quarto não encontrado!', 'error')
        return redirect(url_for('gerenciar_quartos'))
    
    return render_template('admin_quarto_editar.html', quarto=quarto)

@app.route('/admin/quarto/<int:quarto_id>/editar', methods=['POST'])
def processar_edicao_quarto(quarto_id):
    """Processa a edição dos dados do quarto"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    tipo = request.form['tipo'].strip()
    capacidade = request.form['capacidade']
    preco_diaria = request.form['preco_diaria']
    status = request.form['status']
    
    # Validações
    if not tipo or not capacidade or not preco_diaria or not status:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('editar_quarto', quarto_id=quarto_id))
    
    try:
        capacidade = int(capacidade)
        preco_diaria = float(preco_diaria)
    except ValueError:
        flash('Capacidade deve ser um número inteiro e preço deve ser um valor decimal válido!', 'error')
        return redirect(url_for('editar_quarto', quarto_id=quarto_id))
    
    if capacidade <= 0 or preco_diaria <= 0:
        flash('Capacidade e preço devem ser valores positivos!', 'error')
        return redirect(url_for('editar_quarto', quarto_id=quarto_id))
    
    if status not in ['Disponível', 'Ocupado', 'Manutenção']:
        flash('Status inválido!', 'error')
        return redirect(url_for('editar_quarto', quarto_id=quarto_id))
    
    conn = get_db_connection()
    
    # Verificar se quarto tem reservas futuras antes de desativar
    if status == 'Manutenção':
        reservas_futuras = conn.execute('''
            SELECT COUNT(*) FROM reservas 
            WHERE quarto_id = ? AND status IN ('Ativa', 'Concluída') 
            AND data_checkout > date('now')
        ''', (quarto_id,)).fetchone()[0]
        
        if reservas_futuras > 0:
            flash('Não é possível colocar o quarto em manutenção. Existem reservas futuras!', 'error')
            conn.close()
            return redirect(url_for('editar_quarto', quarto_id=quarto_id))
    
    # Atualizar dados
    conn.execute('''
        UPDATE quartos 
        SET tipo = ?, capacidade = ?, preco_diaria = ?, status = ?
        WHERE id = ?
    ''', (tipo, capacidade, preco_diaria, status, quarto_id))
    
    conn.commit()
    conn.close()
    
    flash('Dados do quarto atualizados com sucesso!', 'success')
    return redirect(url_for('gerenciar_quartos'))

@app.route('/admin/quarto/<int:quarto_id>/excluir', methods=['POST'])
def excluir_quarto(quarto_id):
    """Exclui (desativa) um quarto do sistema"""
    if 'admin_id' not in session:
        return redirect(url_for('login_admin'))
        
    conn = get_db_connection()
    
    # RF13: Não permitir exclusão se houver reservas futuras ativas
    reservas_futuras = conn.execute('''
        SELECT COUNT(*) FROM reservas 
        WHERE quarto_id = ? AND status = 'Ativa' 
        AND data_checkout > ?
    ''', (quarto_id, datetime.now().strftime('%Y-%m-%d'))).fetchone()[0]
    
    if reservas_futuras > 0:
        flash('Não é possível excluir quartos com reservas futuras ativas!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_quartos'))
    
    # Exclusão lógica - marca como inativo
    conn.execute('UPDATE quartos SET ativo = 0 WHERE id = ?', (quarto_id,))
    conn.commit()
    conn.close()
    
    flash('Quarto excluído com sucesso!', 'success')
    return redirect(url_for('gerenciar_quartos'))

# ========== ROTAS PARA RESERVAS ==========

@app.route('/admin/reservas')
def gerenciar_reservas():
    """Lista e gerencia reservas"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    # Parâmetros de busca
    busca_hospede = request.args.get('hospede', '').strip()
    busca_quarto = request.args.get('quarto', '').strip()
    busca_status = request.args.get('status', '').strip()
    busca_data = request.args.get('data', '').strip()
    
    conn = get_db_connection()
    
    # Query base com JOIN para pegar dados do hóspede e quarto
    query = '''
        SELECT r.*, h.nome_completo as hospede_nome, h.email as hospede_email,
               q.numero as quarto_numero, q.tipo as quarto_tipo
        FROM reservas r
        JOIN hospedes h ON r.hospede_id = h.id
        JOIN quartos q ON r.quarto_id = q.id
        WHERE 1=1
    '''
    params = []
    
    # Adicionar filtros se informados
    if busca_hospede:
        query += ' AND h.nome_completo LIKE ?'
        params.append(f'%{busca_hospede}%')
    
    if busca_quarto:
        query += ' AND q.numero LIKE ?'
        params.append(f'%{busca_quarto}%')
    
    if busca_status:
        query += ' AND r.status = ?'
        params.append(busca_status)
    
    if busca_data:
        query += ' AND (r.data_checkin <= ? AND r.data_checkout >= ?)'
        params.extend([busca_data, busca_data])
    
    query += ' ORDER BY r.data_checkin DESC'
    
    reservas = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('admin_reservas.html', 
                         reservas=reservas,
                         busca_hospede=busca_hospede,
                         busca_quarto=busca_quarto,
                         busca_status=busca_status,
                         busca_data=busca_data)

@app.route('/admin/reserva/cadastro')
def cadastro_reserva():
    """Formulário de cadastro de reserva"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    hospedes = conn.execute('SELECT * FROM hospedes WHERE ativo = 1 ORDER BY nome_completo').fetchall()
    quartos = conn.execute('SELECT * FROM quartos WHERE ativo = 1 AND status = "Disponível" ORDER BY numero').fetchall()
    conn.close()
    
    return render_template('admin_reserva_cadastro.html', hospedes=hospedes, quartos=quartos)

@app.route('/admin/reserva/cadastro', methods=['POST'])
def processar_cadastro_reserva():
    """Processa o cadastro de nova reserva"""
    if 'admin_id' not in session:
        return redirect(url_for('login_admin'))

    # Obter dados do formulário
    hospede_id = request.form.get('hospede_id', type=int)
    quarto_id = request.form.get('quarto_id', type=int)
    data_checkin_str = request.form.get('data_checkin')
    data_checkout_str = request.form.get('data_checkout')
    numero_hospedes = request.form.get('numero_hospedes', type=int)
    status = request.form.get('status', 'Ativa') # Default para Ativa
    
    # Validações
    if not all([hospede_id, quarto_id, data_checkin_str, data_checkout_str, numero_hospedes, status]):
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('cadastro_reserva'))

    if status not in ['Ativa', 'Concluída', 'Cancelada']:
        flash('Status inválido!', 'error')
        return redirect(url_for('cadastro_reserva'))

    # Checagem explícita para o linter
    if not data_checkin_str or not data_checkout_str:
        flash('As datas de check-in e check-out são obrigatórias.', 'error')
        return redirect(url_for('cadastro_reserva'))

    try:
        data_checkin = datetime.strptime(data_checkin_str, '%Y-%m-%d').date()
        data_checkout = datetime.strptime(data_checkout_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash('Formato de data inválido.', 'error')
        return redirect(url_for('cadastro_reserva'))

    if data_checkin >= data_checkout:
        flash('A data de check-out deve ser posterior à data de check-in.', 'error')
        return redirect(url_for('cadastro_reserva'))

    conn = get_db_connection()

    # Verificar capacidade do quarto
    quarto = conn.execute('SELECT * FROM quartos WHERE id = ?', (quarto_id,)).fetchone()
    if not quarto or numero_hospedes > quarto['capacidade']:
        flash('Número de hóspedes excede a capacidade do quarto ou quarto inválido!', 'error')
        conn.close()
        return redirect(url_for('cadastro_reserva'))

    # Verificar conflitos de reserva
    if status == 'Ativa':
        conflitos = conn.execute('''
            SELECT COUNT(*) FROM reservas 
            WHERE quarto_id = ? AND status = 'Ativa'
            AND NOT (data_checkout <= ? OR data_checkin >= ?)
        ''', (quarto_id, data_checkin_str, data_checkout_str)).fetchone()[0]

        if conflitos > 0:
            flash('Conflito de datas! O quarto já está reservado para este período.', 'error')
            conn.close()
            return redirect(url_for('cadastro_reserva'))

    # Calcular valor total
    duracao_estadia = (data_checkout - data_checkin).days
    valor_total = duracao_estadia * float(quarto['preco_diaria'])

    # Cadastrar reserva
    cursor = conn.execute('''
        INSERT INTO reservas (hospede_id, quarto_id, data_checkin, data_checkout, numero_hospedes, valor_total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (hospede_id, quarto_id, data_checkin_str, data_checkout_str, numero_hospedes, valor_total, status))
    
    reserva_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_operacao('ADMIN_CADASTRO_RESERVA', session['admin_id'], 'admin', f'Reserva ID: {reserva_id} para Hóspede ID: {hospede_id}')
    flash('Reserva cadastrada com sucesso!', 'success')
    return redirect(url_for('gerenciar_reservas'))

@app.route('/admin/reserva/<int:reserva_id>/editar')
def editar_reserva(reserva_id):
    """Formulário para editar reserva"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    reserva = conn.execute('''
        SELECT r.*, h.nome_completo as hospede_nome, q.numero as quarto_numero
        FROM reservas r
        JOIN hospedes h ON r.hospede_id = h.id
        JOIN quartos q ON r.quarto_id = q.id
        WHERE r.id = ?
    ''', (reserva_id,)).fetchone()
    
    if not reserva:
        flash('Reserva não encontrada!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))
    
    hospedes = conn.execute('SELECT * FROM hospedes WHERE ativo = 1 ORDER BY nome_completo').fetchall()
    quartos = conn.execute('SELECT * FROM quartos WHERE ativo = 1 ORDER BY numero').fetchall()
    conn.close()
    
    return render_template('admin_reserva_editar.html', reserva=reserva, hospedes=hospedes, quartos=quartos)

@app.route('/admin/reserva/<int:reserva_id>/editar', methods=['POST'])
def processar_edicao_reserva(reserva_id):
    """Processa a edição dos dados da reserva"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    data_checkin = request.form['data_checkin']
    data_checkout = request.form['data_checkout']
    numero_hospedes = request.form['numero_hospedes']
    status = request.form['status']
    
    # Validações
    if not data_checkin or not data_checkout or not numero_hospedes or not status:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('editar_reserva', reserva_id=reserva_id))
    
    try:
        from datetime import datetime
        checkin = datetime.strptime(data_checkin, '%Y-%m-%d').date()
        checkout = datetime.strptime(data_checkout, '%Y-%m-%d').date()
        numero_hospedes = int(numero_hospedes)
    except ValueError:
        flash('Datas ou número de hóspedes inválidos!', 'error')
        return redirect(url_for('editar_reserva', reserva_id=reserva_id))
    
    if checkin >= checkout:
        flash('Data de check-out deve ser posterior ao check-in!', 'error')
        return redirect(url_for('editar_reserva', reserva_id=reserva_id))
    
    if numero_hospedes <= 0:
        flash('Número de hóspedes deve ser positivo!', 'error')
        return redirect(url_for('editar_reserva', reserva_id=reserva_id))
    
    conn = get_db_connection()
    
    # Obter dados da reserva atual
    reserva_atual = conn.execute('SELECT * FROM reservas WHERE id = ?', (reserva_id,)).fetchone()
    if not reserva_atual:
        flash('Reserva não encontrada!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))
    
    # Verificar capacidade do quarto
    quarto = conn.execute('SELECT * FROM quartos WHERE id = ?', (reserva_atual['quarto_id'],)).fetchone()
    if numero_hospedes > quarto['capacidade']:
        flash('Número de hóspedes excede a capacidade do quarto!', 'error')
        conn.close()
        return redirect(url_for('editar_reserva', reserva_id=reserva_id))
    
    # Verificar conflitos de reserva (excluindo a reserva atual)
    conflitos = conn.execute('''
        SELECT COUNT(*) FROM reservas 
        WHERE quarto_id = ? AND status = 'Ativa' AND id != ?
        AND NOT (data_checkout <= ? OR data_checkin >= ?)
    ''', (reserva_atual['quarto_id'], reserva_id, data_checkin, data_checkout)).fetchone()[0]
    
    if conflitos > 0:
        flash('Já existe uma reserva para este quarto no período selecionado!', 'error')
        conn.close()
        return redirect(url_for('editar_reserva', reserva_id=reserva_id))
    
    # Recalcular valor total
    dias = (checkout - checkin).days
    valor_total = dias * float(quarto['preco_diaria'])
    
    # Atualizar status do quarto se necessário
    if status == 'Concluída' and reserva_atual['status'] != 'Concluída':
        conn.execute('UPDATE quartos SET status = "Disponível" WHERE id = ?', (reserva_atual['quarto_id'],))
    elif status == 'Cancelada' and reserva_atual['status'] != 'Cancelada':
        conn.execute('UPDATE quartos SET status = "Disponível" WHERE id = ?', (reserva_atual['quarto_id'],))
    
    # Atualizar dados da reserva
    conn.execute('''
        UPDATE reservas 
        SET data_checkin = ?, data_checkout = ?, numero_hospedes = ?, 
            valor_total = ?, status = ?
        WHERE id = ?
    ''', (data_checkin, data_checkout, numero_hospedes, valor_total, status, reserva_id))
    
    conn.commit()
    conn.close()
    
    flash('Dados da reserva atualizados com sucesso!', 'success')
    return redirect(url_for('gerenciar_reservas'))

@app.route('/admin/reserva/<int:reserva_id>/cancelar', methods=['POST'])
def cancelar_reserva(reserva_id):
    """Cancela uma reserva"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    
    # Obter dados da reserva
    reserva = conn.execute('SELECT * FROM reservas WHERE id = ?', (reserva_id,)).fetchone()
    if not reserva:
        flash('Reserva não encontrada!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))
    
    # Liberar quarto se estiver ocupado
    if reserva['status'] == 'Concluída':
        conn.execute('UPDATE quartos SET status = "Disponível" WHERE id = ?', (reserva['quarto_id'],))
    
    # Cancelar reserva
    conn.execute('UPDATE reservas SET status = "Cancelada" WHERE id = ?', (reserva_id,))
    conn.commit()
    conn.close()
    
    flash('Reserva cancelada com sucesso!', 'success')
    return redirect(url_for('gerenciar_reservas'))

@app.route('/admin/reserva/<int:reserva_id>/checkin', methods=['POST'])
def processar_checkin(reserva_id):
    """Processa check-in de uma reserva: Apenas muda o status do quarto para Ocupado."""
    if 'admin_id' not in session:
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    reserva = conn.execute('SELECT * FROM reservas WHERE id = ?', (reserva_id,)).fetchone()

    if not reserva:
        flash('Reserva não encontrada!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))

    # Verificar se é possível fazer check-in
    hoje = datetime.now().date()
    data_checkin = datetime.strptime(reserva['data_checkin'], '%Y-%m-%d').date()

    if hoje < data_checkin:
        flash('Check-in só pode ser realizado a partir da data agendada!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))

    if reserva['status'] != 'Ativa':
        flash('Check-in só pode ser realizado em reservas ativas!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))
    
    # Processar check-in: muda status do QUARTO, não da reserva
    conn.execute('UPDATE quartos SET status = "Ocupado" WHERE id = ?', (reserva['quarto_id'],))
    
    conn.commit()
    conn.close()

    log_operacao('CHECKIN_REALIZADO', session['admin_id'], 'admin', f'Reserva ID: {reserva_id}, Quarto ID: {reserva["quarto_id"]}')
    flash('Check-in realizado com sucesso! O quarto agora está marcado como "Ocupado".', 'success')
    return redirect(url_for('gerenciar_reservas'))

@app.route('/admin/reserva/<int:reserva_id>/checkout', methods=['POST'])
def processar_checkout(reserva_id):
    """Processa o check-out de uma reserva: Muda status da reserva para Concluída e do quarto para Disponível"""
    if 'admin_id' not in session:
        return redirect(url_for('login_admin'))

    conn = get_db_connection()
    reserva = conn.execute('SELECT * FROM reservas WHERE id = ?', (reserva_id,)).fetchone()

    if not reserva:
        flash('Reserva não encontrada!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))
    
    # O checkout pode ser feito em qualquer reserva 'Ativa', mesmo antes da data final.
    if reserva['status'] != 'Ativa':
        flash('Só é possível fazer check-out de reservas com status "Ativa"!', 'warning')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))

    # Processar check-out
    conn.execute('UPDATE reservas SET status = "Concluída" WHERE id = ?', (reserva_id,))
    conn.execute('UPDATE quartos SET status = "Disponível" WHERE id = ?', (reserva['quarto_id'],))
    conn.commit()

    log_operacao('CHECKOUT_REALIZADO', session['admin_id'], 'admin', f'Reserva ID: {reserva_id}, Quarto ID: {reserva["quarto_id"]}')
    
    # Notificação para o hóspede
    criar_notificacao(
        reserva['hospede_id'], 
        'hospede', 
        f"Seu check-out da reserva #{reserva_id} foi concluído com sucesso. Esperamos vê-lo novamente!",
        url_for('historico_reservas_hospede')
    )
    
    conn.close()
    flash('Check-out realizado com sucesso!', 'success')
    return redirect(url_for('gerenciar_reservas'))

# ========== ROTAS PARA CONTATO (RF22) ==========

@app.route('/contato')
def contato():
    """Formulário de contato com o hotel"""
    return render_template('contato.html')

@app.route('/contato', methods=['POST'])
def processar_contato():
    """Processa o formulário de contato"""
    nome = request.form['nome'].strip()
    email = request.form['email'].strip().lower()
    assunto = request.form['assunto'].strip()
    mensagem = request.form['mensagem'].strip()
    
    # Validação dos campos
    if not nome or not email or not assunto or not mensagem:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('contato'))
        
    if not validar_email(email):
        flash('Por favor, insira um endereço de e-mail válido.', 'error')
        return redirect(url_for('contato'))

    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO contatos (nome, email, assunto, mensagem) VALUES (?, ?, ?, ?)',
            (nome, email, assunto, mensagem)
        )
        conn.commit()
        conn.close()
        
        # Simula o envio de email para o admin
        detalhes_email = (
            f"Nova mensagem de contato recebida de: {nome} ({email})\n"
            f"Assunto: {assunto}\n"
            f"Mensagem: {mensagem}"
        )
        criar_notificacao(
            session['hospede_id'],
            'hospede',
            f"Nova mensagem de {nome} em Contato.",
            url_for('gerenciar_contatos')
        )

        flash('Sua mensagem foi enviada com sucesso! Entraremos em contato em breve.', 'success')
        return redirect(url_for('index'))

    except sqlite3.Error as e:
        flash(f'Ocorreu um erro ao enviar sua mensagem: {e}', 'error')
        return redirect(url_for('contato'))

# ========== ROTAS PARA HISTÓRICO (RF23) ==========

@app.route('/hospede/historico')
def historico_reservas_hospede():
    """Histórico completo de reservas do hóspede com filtros"""
    if 'hospede_id' not in session:
        flash('Acesso negado! Faça login para ver seu histórico.', 'error')
        return redirect(url_for('login_hospede'))
    
    hospede_id = session['hospede_id']
    
    # Parâmetros de filtro
    filtro_data = request.args.get('data', '').strip()
    filtro_status = request.args.get('status', '').strip()
    filtro_tipo = request.args.get('tipo', '').strip()
    
    conn = get_db_connection()
    
    # Query base
    query = '''
        SELECT r.*, q.numero as quarto_numero, q.tipo as quarto_tipo
        FROM reservas r
        JOIN quartos q ON r.quarto_id = q.id
        WHERE r.hospede_id = ?
    '''
    params = [hospede_id]
    
    # Adicionar filtros
    if filtro_data:
        query += ' AND (r.data_checkin <= ? AND r.data_checkout >= ?)'
        params.extend([filtro_data, filtro_data])
    
    if filtro_status:
        query += ' AND r.status = ?'
        params.append(filtro_status)
    
    if filtro_tipo:
        query += ' AND q.tipo LIKE ?'
        params.append(f'%{filtro_tipo}%')
    
    query += ' ORDER BY r.data_checkin DESC'
    
    reservas_raw = conn.execute(query, params).fetchall()
    conn.close()
    
    # Processar dados para exibição
    reservas = []
    for reserva in reservas_raw:
        reserva_dict = dict(reserva)
        
        # Adicionar informações de período
        checkin = datetime.strptime(reserva['data_checkin'], '%Y-%m-%d').date()
        checkout = datetime.strptime(reserva['data_checkout'], '%Y-%m-%d').date()
        dias = (checkout - checkin).days
        reserva_dict['dias_estadia'] = dias
        
        reservas.append(reserva_dict)
    
    return render_template('hospede_historico.html', 
                         reservas=reservas,
                         filtro_data=filtro_data,
                         filtro_status=filtro_status,
                         filtro_tipo=filtro_tipo)

# ========== ROTAS PARA RELATÓRIOS (RF24) ==========

@app.route('/admin/relatorios')
def relatorios():
    """Painel de relatórios para administradores"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    return render_template('admin_relatorios.html')

@app.route('/admin/relatorio/reservas')
def relatorio_reservas():
    """Relatório de reservas com filtros"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    # Parâmetros de filtro
    data_inicio = request.args.get('data_inicio', '').strip()
    data_fim = request.args.get('data_fim', '').strip()
    status_filtro = request.args.get('status', '').strip()
    hospede_filtro = request.args.get('hospede', '').strip()
    
    conn = get_db_connection()
    
    # Query base
    query = '''
        SELECT r.*, h.nome_completo as hospede_nome, h.email as hospede_email,
               q.numero as quarto_numero, q.tipo as quarto_tipo
        FROM reservas r
        JOIN hospedes h ON r.hospede_id = h.id
        JOIN quartos q ON r.quarto_id = q.id
        WHERE 1=1
    '''
    params = []
    
    # Aplicar filtros
    if data_inicio:
        query += ' AND r.data_checkin >= ?'
        params.append(data_inicio)
    
    if data_fim:
        query += ' AND r.data_checkout <= ?'
        params.append(data_fim)
    
    if status_filtro:
        query += ' AND r.status = ?'
        params.append(status_filtro)
    
    if hospede_filtro:
        query += ' AND h.nome_completo LIKE ?'
        params.append(f'%{hospede_filtro}%')
    
    query += ' ORDER BY r.data_checkin DESC'
    
    reservas_raw = conn.execute(query, params).fetchall()
    conn.close()
    
    # Processar resultados para conversão de data e outros ajustes
    reservas = []
    for r in reservas_raw:
        r_dict = dict(r)
        try:
            # Tenta fazer o parse com e sem microsegundos
            if '.' in r_dict['data_reserva']:
                r_dict['data_reserva'] = datetime.strptime(r_dict['data_reserva'], '%Y-%m-%d %H:%M:%S.%f')
            else:
                r_dict['data_reserva'] = datetime.strptime(r_dict['data_reserva'], '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            logger.warning(f"Não foi possível converter a data '{r_dict['data_reserva']}' para o formato datetime no relatório.")
            r_dict['data_reserva'] = None # Define como None se falhar
        reservas.append(r_dict)

    # Calcular estatísticas
    # [CORREÇÃO] A receita total não deve incluir reservas canceladas
    receita_total = sum(float(r['valor_total']) for r in reservas if r['status'] != 'Cancelada')
    
    estatisticas = {
        'total_reservas': len(reservas),
        'receita_total': receita_total,
        'por_status': {},
        'por_mes': {}
    }
    
    # Agrupar por status
    for reserva in reservas:
        status = reserva['status']
        if status not in estatisticas['por_status']:
            estatisticas['por_status'][status] = 0
        estatisticas['por_status'][status] += 1
    
    return render_template('admin_relatorio_reservas.html', 
                         reservas=reservas,
                         estatisticas=estatisticas,
                         data_inicio=data_inicio,
                         data_fim=data_fim,
                         status_filtro=status_filtro,
                         hospede_filtro=hospede_filtro)

# ========== ROTAS PARA LOGS E AUDITORIA (RNF04) ==========

@app.route('/admin/logs')
def visualizar_logs():
    """Visualização de logs de auditoria (apenas para administradores Master)"""
    if 'admin_id' not in session or session.get('admin_perfil') != 'Master':
        flash('Acesso negado! Apenas administradores Master podem acessar os logs.', 'error')
        return redirect(url_for('painel_admin'))
    
    # Parâmetros de filtro
    filtro_operacao = request.args.get('operacao', '').strip()
    filtro_usuario = request.args.get('usuario', '').strip()
    filtro_data = request.args.get('data', '').strip()
    
    conn = get_db_connection()
    
    # Query base
    query = '''
        SELECT * FROM logs_auditoria
        WHERE 1=1
    '''
    params = []
    
    # Aplicar filtros
    if filtro_operacao:
        query += ' AND operacao LIKE ?'
        params.append(f'%{filtro_operacao}%')
    
    if filtro_usuario:
        query += ' AND (usuario_id = ? OR usuario_tipo LIKE ?)'
        try:
            user_id = int(filtro_usuario)
            params.extend([user_id, f'%{filtro_usuario}%'])
        except ValueError:
            params.extend([0, f'%{filtro_usuario}%'])
    
    if filtro_data:
        query += ' AND DATE(data_operacao) = ?'
        params.append(filtro_data)
    
    query += ' ORDER BY data_operacao DESC LIMIT 1000'
    
    logs = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('admin_logs.html', 
                         logs=logs,
                         filtro_operacao=filtro_operacao,
                         filtro_usuario=filtro_usuario,
                         filtro_data=filtro_data)

# ========== UTILITÁRIOS ==========

@app.route('/admin/contatos')
def gerenciar_contatos():
    """Lista mensagens de contato recebidas"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    contatos = conn.execute('SELECT * FROM contatos ORDER BY data_contato DESC').fetchall()
    conn.close()
    
    return render_template('admin_contatos.html', contatos=contatos)

@app.route('/admin/contato/<int:contato_id>/marcar_respondido', methods=['POST'])
def marcar_contato_respondido(contato_id):
    """Marca um contato como respondido"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    conn.execute('UPDATE contatos SET respondido = 1 WHERE id = ?', (contato_id,))
    conn.commit()
    conn.close()
    
    log_operacao('CONTATO_RESPONDIDO', session['admin_id'], 'admin', f'Contato ID: {contato_id}')
    
    flash('Contato marcado como respondido!', 'success')
    return redirect(url_for('gerenciar_contatos'))

# ========== RF21: NOTIFICAÇÕES DE CHECK-IN (24H) ==========

def verificar_checkins_proximo():
    """Verifica reservas que fazem check-in amanhã e envia notificação"""
    from datetime import datetime, timedelta
    
    amanha = (datetime.now() + timedelta(days=1)).date()
    
    conn = get_db_connection()
    
    # Buscar reservas ativas que fazem check-in amanhã
    reservas = conn.execute('''
        SELECT r.*, h.nome_completo, h.email as hospede_email,
               q.numero as quarto_numero, q.tipo as quarto_tipo
        FROM reservas r
        JOIN hospedes h ON r.hospede_id = h.id
        JOIN quartos q ON r.quarto_id = q.id
        WHERE r.data_checkin = ? AND r.status = 'Ativa'
    ''', (amanha.strftime('%Y-%m-%d'),)).fetchall()
    
    contador_emails = 0
    
    for reserva in reservas:
        # Enviar email de lembrete
        assunto = f'Lembrete: Check-in amanhã - Reserva #{reserva["id"]}'
        detalhes = f'''
        Olá {reserva["nome_completo"]},
        
        Este é um lembrete de que você tem check-in agendado para AMANHÃ ({amanha.strftime("%d/%m/%Y")}).
        
        Detalhes da sua reserva:
        - Reserva: #{reserva["id"]}
        - Quarto: {reserva["quarto_numero"]} ({reserva["quarto_tipo"]})
        - Check-in: {reserva["data_checkin"]} a partir das 14:00h
        - Check-out: {reserva["data_checkout"]} até às 12:00h
        - Hóspedes: {reserva["numero_hospedes"]}
        
        Instruções importantes:
        - Apresente-se na recepção a partir das 14:00h
        - Tenha em mãos um documento com foto
        - Em caso de dúvidas, entre em contato conosco
        
        Aguardamos você!
        
        Hotel Boa Estadia
        Telefone: (35) 3821-0000
        '''
        
        criar_notificacao(
            reserva['hospede_id'],
            'hospede',
            f"Lembrete: Seu check-in para a reserva #{reserva['id']} é amanhã!",
            url_for('minhas_reservas_hospede')
        )
        
        # Registrar log da notificação
        log_operacao('NOTIFICACAO_CHECKIN_24H', reserva['hospede_id'], 'sistema', 
                    f'Reserva #{reserva["id"]}, Check-in: {reserva["data_checkin"]}')
        
        contador_emails += 1
    
    conn.close()
    
    logger.info(f'RF21: {contador_emails} notificações de check-in enviadas para {amanha.strftime("%d/%m/%Y")}')
    return contador_emails

@app.route('/admin/executar_notificacoes_checkin', methods=['POST'])
def executar_notificacoes_checkin():
    """Executa manualmente as notificações de check-in (para desenvolvimento/teste)"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    contador = verificar_checkins_proximo()
    
    if contador > 0:
        flash(f'✅ {contador} notificações de check-in enviadas com sucesso!', 'success')
    else:
        flash('ℹ️ Nenhuma reserva com check-in para amanhã encontrada.', 'info')
    
    return redirect(url_for('painel_admin'))

@app.route('/admin/configurar_notificacoes')
def configurar_notificacoes():
    """Página para configurar as notificações automáticas"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    # Verificar próximas reservas que receberão notificação
    from datetime import datetime, timedelta
    
    amanha = (datetime.now() + timedelta(days=1)).date()
    
    conn = get_db_connection()
    proximas_notificacoes = conn.execute('''
        SELECT r.*, h.nome_completo, h.email as hospede_email,
               q.numero as quarto_numero, q.tipo as quarto_tipo
        FROM reservas r
        JOIN hospedes h ON r.hospede_id = h.id
        JOIN quartos q ON r.quarto_id = q.id
        WHERE r.data_checkin = ? AND r.status = 'Ativa'
        ORDER BY r.id
    ''', (amanha.strftime('%Y-%m-%d'),)).fetchall()
    conn.close()
    
    return render_template('admin_notificacoes.html', 
                         proximas_notificacoes=proximas_notificacoes,
                         data_notificacao=amanha)

def adicionar_logs_reservas():
    """Adiciona logs para operações existentes de reservas"""
    # Esta função já existe no código
    pass

# ========== INICIALIZAÇÃO AUTOMÁTICA ==========

def inicializar_scheduler_notificacoes():
    """Inicializa scheduler para notificações automáticas (em produção usar APScheduler ou Celery)"""
    logger.info("RF21: Sistema de notificações de check-in inicializado")
    logger.info("NOTA: Para produção, implementar com APScheduler ou Celery para execução automática diária")

# ========== SISTEMA DE NOTIFICAÇÕES INTERNAS ==========

def _send_web_push(subscription_info, payload):
    """Função auxiliar para enviar uma notificação push."""
    if not VAPID_PRIVATE_KEY:
        print("Aviso: Chaves VAPID não configuradas. Notificação push não enviada.")
        return
    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS.copy()
        )
    except WebPushException as e:
        if e.response and e.response.status_code == 410:
            print(f"Inscrição expirada: {subscription_info['endpoint']}. Será removida.")
            conn = get_db_connection()
            # Esta é uma forma simples de remover, pode ser otimizada
            conn.execute('DELETE FROM push_subscriptions WHERE subscription_json LIKE ?', (f'%{subscription_info["endpoint"]}%',))
            conn.commit()
            conn.close()
        else:
            print(f"Erro ao enviar notificação push: {e}")

def criar_notificacao(usuario_id, usuario_tipo, mensagem, link=None):
    """Cria uma notificação interna E envia uma notificação push."""
    # 1. Salvar notificação no banco de dados
    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO notificacoes (usuario_id, usuario_tipo, mensagem, link) VALUES (?, ?, ?, ?)',
            (usuario_id, usuario_tipo, mensagem, link)
        )
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar notificação interna: {e}")
    finally:
        if conn:
            conn.close()

    # 2. Enviar notificação push para todos os dispositivos do usuário
    try:
        conn = get_db_connection()
        subscriptions = conn.execute(
            'SELECT subscription_json FROM push_subscriptions WHERE usuario_id = ? AND usuario_tipo = ?',
            (usuario_id, usuario_tipo)
        ).fetchall()
    except Exception as e:
        print(f"Erro ao buscar inscrições push: {e}")
        subscriptions = []
    finally:
        if conn:
            conn.close()
    
    payload = json.dumps({
        'title': 'RESTEL Hotel',
        'body': mensagem,
        'url': url_for('ver_notificacoes', _external=True) # URL completa para o service worker
    })

    for sub in subscriptions:
        _send_web_push(json.loads(sub['subscription_json']), payload)

@app.context_processor
def inject_notifications():
    """Injeta dados de notificação em todos os templates."""
    if 'hospede_id' in session:
        user_id = session['hospede_id']
        user_type = 'hospede'
    elif 'admin_id' in session:
        user_id = session['admin_id']
        user_type = 'admin'
    else:
        return {}

    conn = get_db_connection()
    unread_count = conn.execute(
        'SELECT COUNT(*) FROM notificacoes WHERE usuario_id = ? AND usuario_tipo = ? AND lida = 0',
        (user_id, user_type)
    ).fetchone()[0]
    
    recent_notifications = conn.execute(
        'SELECT * FROM notificacoes WHERE usuario_id = ? AND usuario_tipo = ? ORDER BY data_criacao DESC LIMIT 5',
        (user_id, user_type)
    ).fetchall()
    conn.close()
    
    return dict(unread_count=unread_count, recent_notifications=recent_notifications)

@app.route('/notificacoes')
def ver_notificacoes():
    """Exibe todas as notificações do usuário e as marca como lidas."""
    if 'hospede_id' in session:
        user_id = session['hospede_id']
        user_type = 'hospede'
    elif 'admin_id' in session:
        user_id = session['admin_id']
        user_type = 'admin'
    else:
        flash("Faça login para ver suas notificações.", "error")
        return redirect(url_for('index'))

    conn = get_db_connection()
    # Busca todas as notificações
    notifications_raw = conn.execute(
        'SELECT * FROM notificacoes WHERE usuario_id = ? AND usuario_tipo = ? ORDER BY data_criacao DESC',
        (user_id, user_type)
    ).fetchall()
    
    # Processa as notificações para converter a data
    all_notifications = []
    for n in notifications_raw:
        n_dict = dict(n)
        try:
            # Tenta fazer o parse com e sem microsegundos
            if '.' in n_dict['data_criacao']:
                n_dict['data_criacao'] = datetime.strptime(n_dict['data_criacao'], '%Y-%m-%d %H:%M:%S.%f')
            else:
                n_dict['data_criacao'] = datetime.strptime(n_dict['data_criacao'], '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            # Se falhar, mantém a string original ou um valor padrão
            logger.warning(f"Não foi possível converter a data '{n_dict['data_criacao']}' para o formato datetime.")
            pass # Mantém como string se a conversão falhar
        all_notifications.append(n_dict)

    # Marca todas como lidas
    conn.execute(
        'UPDATE notificacoes SET lida = 1 WHERE usuario_id = ? AND usuario_tipo = ? AND lida = 0',
        (user_id, user_type)
    )
    conn.commit()
    conn.close()
    
    return render_template('notificacoes.html', notifications=all_notifications)

@app.route('/subscribe_push', methods=['POST'])
def subscribe_push():
    """Salva a inscrição de notificação push para o usuário logado."""
    subscription_data = request.get_json()
    if not subscription_data:
        return jsonify({'error': 'Nenhum dado de inscrição recebido'}), 400

    if 'hospede_id' in session:
        user_id = session['hospede_id']
        user_type = 'hospede'
    elif 'admin_id' in session:
        user_id = session['admin_id']
        user_type = 'admin'
    else:
        return jsonify({'error': 'Usuário não autenticado'}), 403

    try:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO push_subscriptions (usuario_id, usuario_tipo, subscription_json) VALUES (?, ?, ?)',
            (user_id, user_type, json.dumps(subscription_data))
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True}), 201
    except sqlite3.IntegrityError:
        # Inscrição já existe, o que é normal.
        return jsonify({'success': True, 'message': 'Inscrição já existe'}), 200
    except Exception as e:
        log_operacao('PUSH_SUBSCRIBE_ERRO', user_id, user_type, str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    inicializar_scheduler_notificacoes()
    app.run(debug=True) 