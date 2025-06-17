from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'restel_secret_key_2025'

# Configurações do banco de dados
import os
DATABASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'restel.db')

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Tabela de hóspedes
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
            hospede_id INTEGER NOT NULL,
            quarto_id INTEGER NOT NULL,
            data_checkin DATE NOT NULL,
            data_checkout DATE NOT NULL,
            numero_hospedes INTEGER NOT NULL,
            valor_total DECIMAL(10,2) NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('Ativa', 'Cancelada', 'Check-in', 'Check-out')),
            data_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hospede_id) REFERENCES hospedes (id),
            FOREIGN KEY (quarto_id) REFERENCES quartos (id)
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
    conn.execute('''
        INSERT INTO hospedes (nome_completo, email, cpf, telefone, senha)
        VALUES (?, ?, ?, ?, ?)
    ''', (nome_completo, email, cpf, telefone, senha_hash))
    
    conn.commit()
    conn.close()
    
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
    reservas_concluidas = conn.execute('SELECT COUNT(*) FROM reservas WHERE hospede_id = ? AND status = "Check-out"', (hospede_id,)).fetchone()[0]
    reservas_canceladas = conn.execute('SELECT COUNT(*) FROM reservas WHERE hospede_id = ? AND status = "Cancelada"', (hospede_id,)).fetchone()[0]
    
    # Próximas reservas
    proximas_reservas = conn.execute('''
        SELECT r.*, q.numero as quarto_numero, q.tipo as quarto_tipo
        FROM reservas r
        JOIN quartos q ON r.quarto_id = q.id
        WHERE r.hospede_id = ? AND r.status IN ('Ativa', 'Check-in')
        AND r.data_checkin >= date('now')
        ORDER BY r.data_checkin ASC
        LIMIT 3
    ''', (hospede_id,)).fetchall()
    
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
    """API que retorna períodos ocupados de um quarto"""
    conn = get_db_connection()
    
    # Buscar reservas ativas do quarto
    reservas = conn.execute('''
        SELECT data_checkin, data_checkout 
        FROM reservas 
        WHERE quarto_id = ? AND status IN ('Ativa', 'Check-in')
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
    """Processa nova reserva feita pelo hóspede"""
    if 'hospede_id' not in session:
        flash('Acesso negado! Faça login para fazer uma reserva.', 'error')
        return redirect(url_for('login_hospede'))
    
    hospede_id = session['hospede_id']
    quarto_id = request.form['quarto_id']
    data_checkin = request.form['data_checkin']
    data_checkout = request.form['data_checkout']
    numero_hospedes = request.form['numero_hospedes']
    
    # Validações
    if not quarto_id or not data_checkin or not data_checkout or not numero_hospedes:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('nova_reserva_hospede'))
    
    try:
        from datetime import datetime
        checkin = datetime.strptime(data_checkin, '%Y-%m-%d').date()
        checkout = datetime.strptime(data_checkout, '%Y-%m-%d').date()
        numero_hospedes = int(numero_hospedes)
    except ValueError:
        flash('Datas ou número de hóspedes inválidos!', 'error')
        return redirect(url_for('nova_reserva_hospede'))
    
    if checkin >= checkout:
        flash('Data de check-out deve ser posterior ao check-in!', 'error')
        return redirect(url_for('nova_reserva_hospede'))
    
    if checkin < datetime.now().date():
        flash('Data de check-in não pode ser no passado!', 'error')
        return redirect(url_for('nova_reserva_hospede'))
    
    if numero_hospedes <= 0:
        flash('Número de hóspedes deve ser positivo!', 'error')
        return redirect(url_for('nova_reserva_hospede'))
    
    conn = get_db_connection()
    
    # Verificar capacidade do quarto
    quarto = conn.execute('SELECT * FROM quartos WHERE id = ?', (quarto_id,)).fetchone()
    if not quarto or numero_hospedes > quarto['capacidade']:
        flash('Número de hóspedes excede a capacidade do quarto!', 'error')
        conn.close()
        return redirect(url_for('nova_reserva_hospede'))
    
    # Verificar conflitos de reserva
    conflitos = conn.execute('''
        SELECT COUNT(*) FROM reservas 
        WHERE quarto_id = ? AND status IN ('Ativa', 'Check-in')
        AND NOT (data_checkout <= ? OR data_checkin >= ?)
    ''', (quarto_id, data_checkin, data_checkout)).fetchone()[0]
    
    if conflitos > 0:
        flash('Já existe uma reserva para este quarto no período selecionado!', 'error')
        conn.close()
        return redirect(url_for('nova_reserva_hospede'))
    
    # Calcular valor total
    dias = (checkout - checkin).days
    valor_total = dias * float(quarto['preco_diaria'])
    
    # Cadastrar reserva
    conn.execute('''
        INSERT INTO reservas (hospede_id, quarto_id, data_checkin, data_checkout, 
                            numero_hospedes, valor_total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (hospede_id, quarto_id, data_checkin, data_checkout, numero_hospedes, valor_total, 'Ativa'))
    
    conn.commit()
    conn.close()
    
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
    from datetime import datetime, timedelta
    hoje = datetime.now().date()
    
    reservas = []
    for reserva in reservas_raw:
        reserva_dict = dict(reserva)
        
        # Verificar regra de 24h
        checkin_date = datetime.strptime(reserva['data_checkin'], '%Y-%m-%d').date()
        limite_edicao = checkin_date - timedelta(days=1)
        
        reserva_dict['pode_editar'] = (
            reserva['status'] == 'Ativa' and 
            hoje < limite_edicao
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
    from datetime import datetime, timedelta
    checkin_date = datetime.strptime(reserva['data_checkin'], '%Y-%m-%d').date()
    hoje = datetime.now().date()
    limite_edicao = checkin_date - timedelta(days=1)
    
    if hoje >= limite_edicao and reserva['status'] == 'Ativa':
        flash('Não é possível editar a reserva. Faltam menos de 24 horas para o check-in!', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))
    
    if reserva['status'] not in ['Ativa']:
        flash('Esta reserva não pode ser editada!', 'error')
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
        WHERE quarto_id = ? AND status IN ('Ativa', 'Check-in') AND id != ?
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
    """Cancela reserva do hóspede"""
    if 'hospede_id' not in session:
        flash('Acesso negado! Faça login para cancelar reservas.', 'error')
        return redirect(url_for('login_hospede'))
    
    hospede_id = session['hospede_id']
    conn = get_db_connection()
    
    # Obter dados da reserva
    reserva = conn.execute('SELECT * FROM reservas WHERE id = ? AND hospede_id = ?', (reserva_id, hospede_id)).fetchone()
    if not reserva:
        flash('Reserva não encontrada!', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))
    
    # Verificar regra de 24h
    from datetime import datetime, timedelta
    checkin_date = datetime.strptime(reserva['data_checkin'], '%Y-%m-%d').date()
    hoje = datetime.now().date()
    limite_cancelamento = checkin_date - timedelta(days=1)
    
    if hoje >= limite_cancelamento and reserva['status'] == 'Ativa':
        flash('Não é possível cancelar a reserva. Faltam menos de 24 horas para o check-in!', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))
    
    if reserva['status'] not in ['Ativa']:
        flash('Esta reserva não pode ser cancelada!', 'error')
        conn.close()
        return redirect(url_for('minhas_reservas_hospede'))
    
    # Cancelar reserva
    conn.execute('UPDATE reservas SET status = "Cancelada" WHERE id = ? AND hospede_id = ?', (reserva_id, hospede_id))
    conn.commit()
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
    
    return render_template('admin_painel.html')

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
            WHERE quarto_id = ? AND status IN ('Ativa', 'Check-in') 
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
    """Exclui (inativa) um quarto"""
    if 'admin_id' not in session:
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    conn = get_db_connection()
    
    # Verificar se quarto tem reservas futuras
    reservas_futuras = conn.execute('''
        SELECT COUNT(*) FROM reservas 
        WHERE quarto_id = ? AND status IN ('Ativa', 'Check-in') 
        AND data_checkout > date('now')
    ''', (quarto_id,)).fetchone()[0]
    
    if reservas_futuras > 0:
        flash('Não é possível excluir o quarto. Existem reservas futuras!', 'error')
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
        flash('Acesso negado! Faça login como administrador.', 'error')
        return redirect(url_for('login_admin'))
    
    hospede_id = request.form['hospede_id']
    quarto_id = request.form['quarto_id']
    data_checkin = request.form['data_checkin']
    data_checkout = request.form['data_checkout']
    numero_hospedes = request.form['numero_hospedes']
    
    # Validações
    if not hospede_id or not quarto_id or not data_checkin or not data_checkout or not numero_hospedes:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('cadastro_reserva'))
    
    try:
        from datetime import datetime
        checkin = datetime.strptime(data_checkin, '%Y-%m-%d').date()
        checkout = datetime.strptime(data_checkout, '%Y-%m-%d').date()
        numero_hospedes = int(numero_hospedes)
    except ValueError:
        flash('Datas ou número de hóspedes inválidos!', 'error')
        return redirect(url_for('cadastro_reserva'))
    
    if checkin >= checkout:
        flash('Data de check-out deve ser posterior ao check-in!', 'error')
        return redirect(url_for('cadastro_reserva'))
    
    if checkin < datetime.now().date():
        flash('Data de check-in não pode ser no passado!', 'error')
        return redirect(url_for('cadastro_reserva'))
    
    if numero_hospedes <= 0:
        flash('Número de hóspedes deve ser positivo!', 'error')
        return redirect(url_for('cadastro_reserva'))
    
    conn = get_db_connection()
    
    # Verificar capacidade do quarto
    quarto = conn.execute('SELECT * FROM quartos WHERE id = ?', (quarto_id,)).fetchone()
    if not quarto or numero_hospedes > quarto['capacidade']:
        flash('Número de hóspedes excede a capacidade do quarto!', 'error')
        conn.close()
        return redirect(url_for('cadastro_reserva'))
    
    # Verificar conflitos de reserva
    conflitos = conn.execute('''
        SELECT COUNT(*) FROM reservas 
        WHERE quarto_id = ? AND status IN ('Ativa', 'Check-in')
        AND NOT (data_checkout <= ? OR data_checkin >= ?)
    ''', (quarto_id, data_checkin, data_checkout)).fetchone()[0]
    
    if conflitos > 0:
        flash('Já existe uma reserva para este quarto no período selecionado!', 'error')
        conn.close()
        return redirect(url_for('cadastro_reserva'))
    
    # Calcular valor total
    dias = (checkout - checkin).days
    valor_total = dias * float(quarto['preco_diaria'])
    
    # Cadastrar reserva
    conn.execute('''
        INSERT INTO reservas (hospede_id, quarto_id, data_checkin, data_checkout, 
                            numero_hospedes, valor_total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (hospede_id, quarto_id, data_checkin, data_checkout, numero_hospedes, valor_total, 'Ativa'))
    
    conn.commit()
    conn.close()
    
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
    
    if status not in ['Ativa', 'Cancelada', 'Check-in', 'Check-out']:
        flash('Status inválido!', 'error')
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
        WHERE quarto_id = ? AND status IN ('Ativa', 'Check-in') AND id != ?
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
    if status == 'Check-in' and reserva_atual['status'] != 'Check-in':
        conn.execute('UPDATE quartos SET status = "Ocupado" WHERE id = ?', (reserva_atual['quarto_id'],))
    elif status == 'Check-out' and reserva_atual['status'] != 'Check-out':
        conn.execute('UPDATE quartos SET status = "Disponível" WHERE id = ?', (reserva_atual['quarto_id'],))
    elif status in ['Ativa', 'Cancelada'] and reserva_atual['status'] == 'Check-in':
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
    if reserva['status'] == 'Check-in':
        conn.execute('UPDATE quartos SET status = "Disponível" WHERE id = ?', (reserva['quarto_id'],))
    
    # Cancelar reserva
    conn.execute('UPDATE reservas SET status = "Cancelada" WHERE id = ?', (reserva_id,))
    conn.commit()
    conn.close()
    
    flash('Reserva cancelada com sucesso!', 'success')
    return redirect(url_for('gerenciar_reservas'))

@app.route('/admin/reserva/<int:reserva_id>/checkin', methods=['POST'])
def processar_checkin(reserva_id):
    """Processa check-in de uma reserva"""
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
    
    # Verificar se é possível fazer check-in
    from datetime import datetime
    hoje = datetime.now().date()
    checkin_date = datetime.strptime(reserva['data_checkin'], '%Y-%m-%d').date()
    
    if hoje < checkin_date:
        flash('Check-in só pode ser realizado a partir da data agendada!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))
    
    if reserva['status'] != 'Ativa':
        flash('Check-in só pode ser realizado em reservas ativas!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))
    
    # Processar check-in
    conn.execute('UPDATE reservas SET status = "Check-in" WHERE id = ?', (reserva_id,))
    conn.execute('UPDATE quartos SET status = "Ocupado" WHERE id = ?', (reserva['quarto_id'],))
    
    conn.commit()
    conn.close()
    
    flash('Check-in realizado com sucesso!', 'success')
    return redirect(url_for('gerenciar_reservas'))

@app.route('/admin/reserva/<int:reserva_id>/checkout', methods=['POST'])
def processar_checkout(reserva_id):
    """Processa check-out de uma reserva"""
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
    
    # Verificar se é possível fazer check-out
    if reserva['status'] != 'Check-in':
        flash('Check-out só pode ser realizado após check-in!', 'error')
        conn.close()
        return redirect(url_for('gerenciar_reservas'))
    
    # Processar check-out
    conn.execute('UPDATE reservas SET status = "Check-out" WHERE id = ?', (reserva_id,))
    conn.execute('UPDATE quartos SET status = "Disponível" WHERE id = ?', (reserva['quarto_id'],))
    
    conn.commit()
    conn.close()
    
    flash('Check-out realizado com sucesso!', 'success')
    return redirect(url_for('gerenciar_reservas'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 