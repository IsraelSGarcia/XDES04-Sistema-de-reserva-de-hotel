# 🛠️ Documentação para Desenvolvedores - RESTEL

## 📋 Guia de Desenvolvimento

Este documento contém informações técnicas para desenvolvedores que trabalham no sistema RESTEL.

## 🏗️ Arquitetura do Sistema

### Estrutura de Pastas
```
restel/
├── src/restel/          # Código principal da aplicação
│   ├── app.py          # Aplicação Flask principal
│   └── templates/      # Templates HTML Jinja2
├── tests/              # Testes automatizados
├── data/               # Banco de dados SQLite
├── static/             # Recursos estáticos (CSS, JS, imagens)
├── scripts/            # Scripts utilitários
├── docs/               # Documentação técnica
└── logs/               # Logs da aplicação
```

### Padrões de Código

#### Backend (Python/Flask)
- **Framework:** Flask 2.3.3
- **Banco:** SQLite com SQLAlchemy patterns
- **Autenticação:** Flask sessions + Werkzeug password hashing
- **Validação:** Validações server-side em Python

#### Frontend
- **HTML:** Templates Jinja2 com herança
- **CSS:** Bootstrap 5 + CSS customizado
- **JavaScript:** Vanilla JS para validações e interações

## 🔧 Configuração de Desenvolvimento

### Pré-requisitos
```bash
# Python 3.7+
python --version

# pip atualizado
python -m pip install --upgrade pip
```

### Setup Automático
```bash
# Executa configuração completa
python setup_dev.py
```

### Setup Manual
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar banco
python src/restel/app.py  # Cria banco automaticamente

# Executar aplicação
python src/restel/app.py
```

## 🧪 Testes

### Executar Testes
```bash
# Interface interativa (recomendado)
python test_runner.py

# Comando direto
pytest tests/ -v

# Teste específico
pytest tests/test_guest_crud.py -v

# Com relatório HTML
pytest tests/ --html=tests/reports/report.html --self-contained-html
```

### Estrutura de Testes
- **Unitários:** `test_simple.py`
- **Integração:** `test_routes.py`
- **CRUD Hóspedes:** `test_guest_crud.py`
- **CRUD Admins:** `test_admin_crud.py`
- **Page Objects:** `tests/pages/`
- **Utilitários:** `tests/utils/`

## 🗃️ Banco de Dados

### Schema Principal

#### Tabela: hospedes
```sql
CREATE TABLE hospedes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_completo TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    cpf TEXT UNIQUE NOT NULL,
    telefone TEXT NOT NULL,
    senha TEXT NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Tabela: administradores
```sql
CREATE TABLE administradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_completo TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL CHECK(perfil IN ('Master', 'Padrão')),
    ativo BOOLEAN DEFAULT 1,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Operações Comuns
```python
# Conexão
conn = sqlite3.connect('data/restel.db')
conn.row_factory = sqlite3.Row

# Query com parâmetros
cursor.execute('SELECT * FROM hospedes WHERE email = ?', (email,))

# Insert seguro
cursor.execute('''
    INSERT INTO hospedes (nome_completo, email, cpf, telefone, senha)
    VALUES (?, ?, ?, ?, ?)
''', (nome, email, cpf, telefone, hash_senha))
```

## 🔒 Segurança

### Autenticação
```python
# Hash de senha
from werkzeug.security import generate_password_hash, check_password_hash

senha_hash = generate_password_hash('senha123')
is_valid = check_password_hash(senha_hash, 'senha123')
```

### Sessões
```python
# Criar sessão
session['admin_id'] = admin['id']
session['admin_perfil'] = admin['perfil']

# Verificar autorização
if 'admin_id' not in session:
    return redirect(url_for('login_admin'))
```

### Validações
```python
# CPF
def validar_cpf(cpf):
    cpf = re.sub('[^0-9]', '', cpf)
    return len(cpf) == 11 and cpf.isdigit()

# Email
def validar_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None
```

## 🌐 Rotas da API

### Públicas
```python
@app.route('/')                    # Página inicial
@app.route('/hospede/cadastro')    # Cadastro de hóspede
```

### Administrativas
```python
@app.route('/admin/login')                           # Login admin
@app.route('/admin/painel')                          # Dashboard
@app.route('/admin/hospedes')                        # Gerenciar hóspedes
@app.route('/admin/administradores')                 # Gerenciar admins
@app.route('/admin/hospede/<int:id>/editar')        # Editar hóspede
@app.route('/admin/administrador/<int:id>/editar')  # Editar admin
```

## 🎨 Templates

### Hierarquia
```
base.html                    # Template base
├── index.html              # Página inicial
├── hospede_cadastro.html   # Cadastro hóspede
└── admin/
    ├── admin_login.html    # Login admin
    ├── admin_painel.html   # Dashboard
    ├── admin_hospedes.html # Lista hóspedes
    └── ...
```

### Blocos Principais
```html
<!-- base.html -->
{% block title %}{% endblock %}
{% block extra_css %}{% endblock %}
{% block content %}{% endblock %}
{% block extra_js %}{% endblock %}
```

## 🚀 Deploy

### Desenvolvimento
```bash
# Aplicação Flask
python src/restel/app.py
# Acesso: http://localhost:5000
```

### Produção (Sugestões)
```bash
# Com Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 src.restel.app:app

# Variáveis de ambiente
export FLASK_ENV=production
export SECRET_KEY="chave-super-secreta"
```

## 🐛 Debug e Troubleshooting

### Logs
```python
# Habilitar debug
app.debug = True

# Logs customizados
import logging
logging.basicConfig(level=logging.INFO)
```

### Problemas Comuns

1. **Banco não encontrado**
   ```bash
   python setup_dev.py  # Recria estrutura
   ```

2. **Erro de importação**
   ```bash
   # Verificar PYTHONPATH
   echo $PYTHONPATH
   ```

3. **Testes falhando**
   ```bash
   # Limpar cache
   python test_runner.py  # Opção 8
   ```

## 📚 Recursos Adicionais

### Dependências
- **Flask:** Framework web
- **Werkzeug:** Utilitários web/segurança  
- **pytest:** Framework de testes
- **selenium:** Testes de browser
- **webdriver-manager:** Gestão de drivers

### Links Úteis
- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Bootstrap 5](https://getbootstrap.com/)

---

**Desenvolvido com 💚 para o Hotel Boa Estadia** 