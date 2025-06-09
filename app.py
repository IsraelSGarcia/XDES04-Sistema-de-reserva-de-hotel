from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'restel_secret_key_2025'

# Configurações do banco de dados
DATABASE = 'restel.db'

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
    conn = sqlite3.connect(DATABASE)
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
    # Debug: print form data
    print("Form data received:", dict(request.form))
    print("Content-Type:", request.content_type)
    
    # Safely get form data with error handling
    nome_completo = request.form.get('nome_completo', '').strip()
    email = request.form.get('email', '').strip().lower()
    cpf = re.sub('[^0-9]', '', request.form.get('cpf', ''))
    telefone = request.form.get('telefone', '').strip()
    senha = request.form.get('senha', '')
    
    # Validações
    if not nome_completo or not email or not cpf or not telefone or not senha:
        flash('Todos os campos são obrigatórios!', 'error')
        return redirect(url_for('cadastro_hospede'))
    
    if not validar_email(email):
        flash('Email inválido!', 'error')
        return redirect(url_for('cadastro_hospede'))
    
    if not validar_cpf(cpf):
        flash('CPF inválido!', 'error')
        return redirect(url_for('cadastro_hospede'))
    
    if len(senha) < 6:
        flash('Senha deve ter pelo menos 6 caracteres!', 'error')
        return redirect(url_for('cadastro_hospede'))
    
    conn = get_db_connection()
    
    # Verificar se email já existe
    if conn.execute('SELECT id FROM hospedes WHERE email = ?', (email,)).fetchone():
        flash('Email já cadastrado!', 'error')
        conn.close()
        return redirect(url_for('cadastro_hospede'))
    
    # Verificar se CPF já existe
    if conn.execute('SELECT id FROM hospedes WHERE cpf = ?', (cpf,)).fetchone():
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 