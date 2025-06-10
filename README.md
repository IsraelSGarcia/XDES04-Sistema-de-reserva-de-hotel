# RESTEL - Sistema de Reserva de Hotel

**Sistema de Gerenciamento de Hóspedes e Administradores**

Sistema completo para gerenciamento de hóspedes e administradores do sistema RESTEL do Hotel Boa Estadia.

## 🎯 Funcionalidades Disponíveis

### Gerenciamento de Hóspedes
- Cadastro de Hóspedes
- Consulta de Hóspedes com filtros (nome, CPF, email, status)
- Atualização de dados do hóspede (exceto CPF)
- Controle de status de hóspedes

### Gerenciamento de Administradores
- Cadastro de Administradores (apenas Master)
- Login de Administrador
- Consulta de Administradores
- Atualização de Administrador
- Controle de status de Administrador

## 🚀 Como Executar

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Configuração Rápida

1. **🚀 Inicialização Simples (Novo!)**
   ```bash
   # Script principal com todas as opções
   python tools/iniciar.py
   ```
   
   **Interface unificada com:**
   - Configuração automática do ambiente
   - Executor de testes interativo  
   - Inicialização da aplicação web
   - Status do projeto em tempo real
   - Acesso à documentação
   - Ferramentas de desenvolvimento

2. **⚙️ Configuração Automática**
   ```bash
   # Script de configuração (100% em português)
   python tools/setup_dev.py
   ```

3. **🔧 Configuração Manual (Alternativa)**
   ```bash
   # Instale as dependências
   pip install -r config/requirements.txt
   
   # Execute a aplicação
   python src/restel/app.py
   ```

3. **Acesse no navegador**
   ```
   http://localhost:5000
   ```

## 📁 Estrutura do Projeto (Organizada e Limpa)

```
restel/
├── 📱 src/restel/              # Aplicação principal
│   ├── app.py                 # Aplicação Flask principal
│   └── templates/             # Templates HTML Jinja2
├── 🧪 tests/                   # Suíte de testes
│   ├── conftest.py            # Configuração de testes
│   ├── test_admin_crud.py     # Testes CRUD administradores
│   ├── test_guest_crud.py     # Testes CRUD hóspedes
│   ├── test_routes.py         # Testes de rotas
│   ├── test_simple.py         # Testes unitários
│   ├── pages/                 # Page Objects (Selenium)
│   ├── utils/                 # Utilitários de teste
│   ├── reports/               # Relatórios HTML (auto-limpeza)
│   └── screenshots/           # Screenshots de falhas
├── 🔧 tools/                   # Ferramentas de desenvolvimento
│   ├── iniciar.py             # Script principal de entrada
│   ├── setup_dev.py           # Configuração de ambiente
│   └── test_runner.py         # Executor de testes interativo
├── ⚙️ config/                  # Configurações do projeto
│   ├── pytest.ini            # Configuração pytest
│   ├── pyrightconfig.json     # Configuração Pyright
│   ├── requirements.txt       # Dependências principais
│   └── requirements-test.txt  # Dependências de teste
├── 💾 data/                    # Banco de dados
│   └── restel.db              # SQLite database
├── 🎨 static/                  # Recursos web estáticos
│   ├── css/                   # Arquivos CSS
│   ├── js/                    # Arquivos JavaScript
│   └── images/                # Imagens
├── 📚 docs/                    # Documentação
│   ├── DESENVOLVIMENTO.md     # Guia técnico completo
│   └── CLEANUP_PLAN.md        # Histórico de organização
├── 📜 scripts/                 # Scripts legados/utilitários
├── 📝 logs/                    # Logs da aplicação
├── 📋 README.md                # Este arquivo
└── 🔒 .gitignore              # Controle de versão
```

## 🧪 Testes Automatizados

O projeto inclui uma suíte abrangente de testes com um executor interativo.

### Executor de Testes Interativo

```bash
python tools/test_runner.py
# ou através do script principal
python tools/iniciar.py  # opção 2
```

O executor de testes agora está **100% em português** com interface intuitiva:

**Funcionalidades:**
- 🚀 Executar todos os testes
- 🧪 Apenas testes unitários
- 🔗 Testes de integração
- 👤 Testes CRUD de hóspedes
- 🔐 Testes CRUD de administradores
- 🌐 Testes de rotas
- 📊 Geração de relatório HTML
- 🧹 Limpeza de cache
- ❓ Ajuda e informações de teste

**Interface em Português:**
- Todas as mensagens e prompts em português
- Comandos traduzidos e localizados
- Feedback claro sobre execução dos testes

### Testes Manuais

```bash
# Executar todos os testes
pytest tests/ -v

# Executar arquivo específico de teste
pytest tests/test_guest_crud.py -v

# Gerar relatório HTML
pytest tests/ --html=tests/reports/report.html --self-contained-html
```

### Testes com Selenium IDE (Legado)

Para compatibilidade com testes antigos, você pode usar o Selenium IDE:

1. **Instale a extensão Selenium IDE** no seu navegador
   - [Chrome](https://chrome.google.com/webstore/detail/selenium-ide/mooikfkahbdckldjjndioackbalphokd)
   - [Firefox](https://addons.mozilla.org/en-US/firefox/addon/selenium-ide/)

2. **Execute a aplicação**
   ```bash
   python src/restel/app.py
   ```

3. **Importe testes antigos** se houver arquivos `.side` disponíveis

## 🔐 Credenciais de Acesso

### Administrador Master Padrão
- **Email:** admin@restel.com
- **Senha:** admin123

Use estas credenciais para acessar o painel administrativo e gerenciar o sistema.

## 📱 Interface

- **Design Responsivo:** Compatível com desktop, tablet e mobile
- **Interface Moderna:** Bootstrap 5 com ícones Font Awesome
- **Navegação Intuitiva:** Menu claro e feedback visual
- **Validações em Tempo Real:** Máscaras e validações JavaScript

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python Flask
- **Banco de Dados:** SQLite (local)
- **Frontend:** HTML5, CSS3, JavaScript
- **Framework CSS:** Bootstrap 5
- **Ícones:** Font Awesome
- **Segurança:** Werkzeug password hashing
- **Testes:** pytest, Selenium WebDriver
- **Automação:** Scripts Python 100% em português
- **Interface:** Menus interativos com emojis e feedback em português

## 📊 Estrutura do Banco de Dados

### Tabela: hospedes
- id (PK)
- nome_completo
- email (único)
- cpf (único)
- telefone
- senha (hash)
- ativo (boolean)
- data_cadastro

### Tabela: administradores
- id (PK)
- nome_completo
- email (único)
- senha (hash)
- perfil (Master/Padrão)
- ativo (boolean)
- data_cadastro

## 🔒 Segurança Implementada

- **Senhas Criptografadas:** Werkzeug PBKDF2 hashing
- **Validação de CPF:** Formato e unicidade
- **Sessões Seguras:** Flask sessions com chave secreta
- **Controle de Acesso:** Permissões por perfil de administrador
- **Validação de Email:** Formato e unicidade
- **Preservação de Dados:** Histórico mantido para auditoria

## 🎮 Como Usar

### Para Hóspedes
1. Acesse a página inicial
2. Clique em "Cadastrar-se como Hóspede"
3. Preencha todos os dados obrigatórios
4. Confirme o cadastro

### Para Administradores
1. Acesse "Login Admin" no menu
2. Use as credenciais padrão ou crie novos admins
3. No painel administrativo, acesse:
   - **Gerenciar Hóspedes:** Visualizar, editar e controlar status
   - **Gerenciar Administradores:** (apenas Master)

### Perfis de Administrador
- **Master:** Acesso total, pode gerenciar outros administradores
- **Padrão:** Apenas gerenciamento de hóspedes

## 📋 Recursos do Sistema

- Interface intuitiva e fácil de usar
- Feedback visual claro em todas as operações
- Compatibilidade com dispositivos móveis
- Controle de acesso por perfil
- Suíte de testes abrangente e interativa
- Configuração automática de ambiente de desenvolvimento

## 🔍 Solução de Problemas

### Problemas Comuns

1. **Banco de dados não encontrado**
   ```bash
   python setup_dev.py
   ```

2. **Erros de importação**
   - Verifique o caminho do Python
   - Certifique-se de estar na raiz do projeto

3. **Falhas nos testes**
   - Execute testes individuais para isolar problemas
   - Verifique o estado do banco de dados
   - Confirme as dependências

### Logs

Os logs da aplicação são armazenados no diretório `logs/`.

## 🔮 Funcionalidades Futuras

Para expansão do sistema, podem ser implementadas:
- Gerenciamento de quartos
- Sistema de reservas
- Check-in/Check-out
- Relatórios avançados
- Notificações por email
- Histórico de reservas
- API REST completa

## 📞 Informações do Projeto

- **Cliente:** Hotel Boa Estadia
- **Desenvolvedor:** SWFactory Consultoria e Sistemas Ltda
- **Versão:** 2.0 (Reorganizada e Otimizada)

## 🐛 Suporte

Em caso de problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme que o Python 3.7+ está sendo usado
3. Certifique-se de que a porta 5000 está disponível
4. O banco SQLite será criado automaticamente na primeira execução
5. Use o executor de testes interativo para diagnosticar problemas

---

**Sistema RESTEL - Transformando a gestão hoteleira! 🏨** 