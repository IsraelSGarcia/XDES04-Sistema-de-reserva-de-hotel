# 🧪 Testes Automatizados do RESTEL

Sistema completo de testes automatizados para o RESTEL - Sistema de Reserva de Hotel, utilizando **Selenium WebDriver** e **pytest**.

## 📋 Índice

- [Estrutura dos Testes](#estrutura-dos-testes)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Execução dos Testes](#execução-dos-testes)
- [Tipos de Testes](#tipos-de-testes)
- [Page Objects](#page-objects)
- [Relatórios](#relatórios)
- [Configuração](#configuração)
- [Troubleshooting](#troubleshooting)

## 🏗️ Estrutura dos Testes

```
tests/
├── __init__.py                 # Inicialização do pacote
├── conftest.py                 # Configurações globais do pytest
├── pytest.ini                 # Configurações do pytest
├── README.md                   # Esta documentação
│
├── pages/                      # Page Objects
│   ├── __init__.py
│   ├── base_page.py           # Classe base para Page Objects
│   ├── guest_pages.py         # Page Objects para hóspedes
│   └── admin_pages.py         # Page Objects para administradores
│
├── test_guest_crud.py         # Testes CRUD de hóspedes
├── test_admin_crud.py         # Testes CRUD de administradores
│
├── utils/                     # Utilitários de teste
│   ├── __init__.py
│   └── test_helpers.py        # Helpers e utilitários
│
├── screenshots/               # Screenshots de falhas
├── reports/                   # Relatórios HTML gerados
└── logs/                      # Logs de execução
```

## 🔧 Pré-requisitos

### Dependências do Sistema
- **Python 3.8+**
- **Google Chrome** (recomendado) ou Firefox
- **ChromeDriver** (instalado automaticamente via webdriver-manager)

### Dependências Python
Todas as dependências estão listadas em `requirements.txt`:

```
Flask==2.3.3
Werkzeug==2.3.7
selenium==4.15.2
pytest==7.4.3
pytest-html==4.1.1
webdriver-manager==4.0.1
```

## 🚀 Instalação

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Verificar Instalação
```bash
python run_tests.py --install-deps
```

## ▶️ Execução dos Testes

### Método Rápido (Script Principal)

```bash
# Executa todos os testes
python run_tests.py

# Executa apenas testes de hóspedes
python run_tests.py --type guest

# Executa apenas testes de administradores
python run_tests.py --type admin

# Executa com browser visível (não headless)
python run_tests.py --visible

# Executa e verifica se Flask está rodando
python run_tests.py --check-flask
```

### Método Pytest (Direto)

```bash
# Executa todos os testes
pytest tests/ -v

# Executa testes específicos
pytest tests/test_guest_crud.py -v
pytest tests/test_admin_crud.py -v

# Executa com marcadores
pytest -m "guest" -v
pytest -m "admin" -v

# Gera relatório HTML
pytest tests/ --html=reports/report.html --self-contained-html
```

## 🎯 Tipos de Testes

### 🏠 Testes de Hóspedes (`test_guest_crud.py`)

| Teste | Descrição |
|-------|-----------|
| `test_create_guest_valid_data` | Criação com dados válidos |
| `test_create_guest_invalid_data` | Criação com dados inválidos |
| `test_read_guest_list` | Listagem de hóspedes |
| `test_search_guest` | Busca de hóspedes |
| `test_update_guest` | Atualização de dados |
| `test_delete_guest` | Exclusão lógica |
| `test_guest_form_validation` | Validação de formulários |
| `test_edit_guest_form_prepopulation` | Preenchimento automático |
| `test_cancel_guest_edit` | Cancelamento de edição |
| `test_search_no_results` | Busca sem resultados |

### 👨‍💼 Testes de Administradores (`test_admin_crud.py`)

| Teste | Descrição |
|-------|-----------|
| `test_admin_login_valid_credentials` | Login com credenciais válidas |
| `test_admin_login_invalid_credentials` | Login com credenciais inválidas |
| `test_create_admin_valid_data` | Criação com dados válidos |
| `test_create_admin_invalid_data` | Criação com dados inválidos |
| `test_read_admin_list` | Listagem de administradores |
| `test_search_admin` | Busca de administradores |
| `test_update_admin` | Atualização de dados |
| `test_delete_admin` | Exclusão lógica |
| `test_admin_form_validation` | Validação de formulários |
| `test_edit_admin_form_prepopulation` | Preenchimento automático |
| `test_cancel_admin_edit` | Cancelamento de edição |
| `test_search_no_results` | Busca sem resultados |
| `test_admin_panel_navigation` | Navegação no painel |
| `test_different_admin_profiles` | Perfis Master e Standard |

## 🎭 Page Objects

### Arquitetura
Os Page Objects encapsulam a interação com elementos da interface, proporcionando:

- **Manutenibilidade**: Mudanças na UI requerem alterações apenas nos Page Objects
- **Reutilização**: Métodos comuns podem ser compartilhados
- **Legibilidade**: Testes mais limpos e expressivos

### Classes Principais

#### `BasePage`
Classe base com métodos comuns:
- `find_element()` - Localiza elementos com espera explícita
- `click()` - Clica em elementos com validação
- `send_keys()` - Envia texto para campos
- `wait_for_url_contains()` - Aguarda mudança de URL

#### `GuestRegistrationPage`
- `register_guest()` - Processo completo de registro
- `fill_form()` - Preenchimento do formulário
- `get_success_message()` - Obtenção de mensagens

#### `AdminLoginPage`
- `login()` - Processo de autenticação
- `get_error_message()` - Tratamento de erros

## 📊 Relatórios

### Relatórios HTML
Os testes geram relatórios HTML automáticos com:

- **Resumo de execução** (passaram/falharam)
- **Duração de cada teste**
- **Screenshots de falhas**
- **Logs detalhados**
- **Gráficos de resultados**

### Localização
```
tests/reports/report_YYYYMMDD_HHMMSS.html
```

### Screenshots
Capturas automáticas em caso de falhas:
```
tests/screenshots/failure_test_name_timestamp.png
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Executar sem headless
export PYTEST_BROWSER_HEADLESS=false

# URL base da aplicação
export RESTEL_BASE_URL=http://localhost:5000
```

### Configuração do Browser

No arquivo `conftest.py`, você pode ajustar:

```python
# Para executar com browser visível
chrome_options.add_argument("--headless")  # Remova esta linha

# Para diferentes resoluções
chrome_options.add_argument("--window-size=1920,1080")

# Para debugging
chrome_options.add_argument("--enable-logging")
chrome_options.add_argument("--log-level=0")
```

### Timeouts

Ajuste timeouts no `conftest.py`:

```python
# Timeout padrão para elementos
driver.implicitly_wait(10)

# Timeout para WebDriverWait
WebDriverWait(driver, 10)
```

## 🔍 Debugging

### Execução com Browser Visível
```bash
python run_tests.py --visible
```

### Logs Detalhados
```bash
pytest tests/ -v --log-cli-level=DEBUG
```

### Breakpoints
Adicione breakpoints no código dos testes:
```python
import pdb; pdb.set_trace()
```

### Screenshots Manuais
```python
driver.save_screenshot("debug_screenshot.png")
```

## 🛠️ Troubleshooting

### Problemas Comuns

#### ❌ ChromeDriver não encontrado
**Solução**: O webdriver-manager instala automaticamente. Se persistir:
```bash
pip install --upgrade webdriver-manager
```

#### ❌ Aplicação Flask não está rodando
**Solução**: 
1. Inicie a aplicação em outro terminal: `python app.py`
2. Ou use: `python run_tests.py --check-flask`

#### ❌ Timeout nos elementos
**Solução**: Aumente o timeout no `conftest.py`:
```python
driver.implicitly_wait(20)  # Era 10, aumentar para 20
```

#### ❌ Testes intermitentes
**Solução**: Adicione `time.sleep()` ou melhore as esperas explícitas:
```python
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "elemento"))
)
```

### Logs de Debug

Para análise detalhada de falhas:

```bash
# Executa com logs detalhados
pytest tests/ -v --log-cli-level=DEBUG --capture=no

# Salva logs em arquivo
pytest tests/ -v --log-file=tests/logs/test_debug.log
```

## 📋 Checklist de Execução

Antes de executar os testes:

- [ ] ✅ Python 3.8+ instalado
- [ ] ✅ Dependências instaladas (`pip install -r requirements.txt`)
- [ ] ✅ Chrome/Firefox atualizado
- [ ] ✅ Aplicação Flask rodando (`python app.py`)
- [ ] ✅ Porta 5000 disponível
- [ ] ✅ Banco de dados SQLite acessível

## 🚀 Execução Rápida

Para execução completa dos testes:

```bash
# 1. Instalar dependências e verificar ambiente
python run_tests.py --install-deps --check-flask

# 2. Executar todos os testes com relatório
python run_tests.py --visible

# 3. Executar apenas smoke tests
python run_tests.py --type smoke
```

## 📞 Suporte

Em caso de problemas:

1. Verifique os logs em `tests/logs/`
2. Analise screenshots em `tests/screenshots/`
3. Consulte o relatório HTML mais recente
4. Execute com `--visible` para debugging visual

---

**Desenvolvido para RESTEL - Sistema de Reserva de Hotel** 🏨 