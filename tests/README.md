# 🧪 Testes Automatizados - Sistema RESTEL

## 📋 Visão Geral

Sistema de testes completamente reorganizado e modularizado para o projeto RESTEL. Esta nova estrutura oferece flexibilidade, organização e facilidade de manutenção.

## 🏗️ Estrutura Organizada

```
tests/
├── config/              # Configurações centralizadas
│   ├── conftest.py     # Fixtures principais e configuração
│   └── pytest.ini     # Configuração do pytest
│
├── unit/               # Testes unitários
│   └── test_simple.py  # Testes básicos do sistema
│
├── integration/        # Testes de integração
│   └── test_auth_integration.py  # Fluxos de autenticação
│
├── e2e/               # Testes end-to-end (Selenium)
│   ├── test_admin_crud.py
│   └── test_guest_crud.py
│
├── api/               # Testes de API/rotas
│   └── test_routes.py
│
├── fixtures/          # Fixtures organizadas
│   ├── __init__.py
│   ├── database_fixtures.py
│   ├── auth_fixtures.py
│   └── data_fixtures.py
│
├── helpers/           # Utilitários e funções auxiliares
│   ├── __init__.py
│   └── test_helpers.py
│
├── pages/             # Page Objects para Selenium
│   └── (arquivos de page objects)
│
├── reports/           # Relatórios gerados
├── screenshots/       # Screenshots de falhas
└── README.md         # Esta documentação
```

## 🎯 Categorias de Teste

### 🧪 Testes Unitários (`/unit/`)
- Verificações básicas de componentes isolados
- Importações e configurações
- Funcionalidades individuais
- **Marcadores**: `@pytest.mark.unit`, `@pytest.mark.smoke`

### 🔗 Testes de Integração (`/integration/`)
- Fluxos completos entre componentes
- Interações banco de dados + aplicação
- Autenticação e autorização
- **Marcadores**: `@pytest.mark.integration`, `@pytest.mark.auth`

### 🌐 Testes End-to-End (`/e2e/`)
- Simulação completa de uso real
- Interface gráfica com Selenium
- Jornadas de usuário completas
- **Marcadores**: `@pytest.mark.e2e`, `@pytest.mark.ui`

### 🚀 Testes de API (`/api/`)
- Endpoints e rotas HTTP
- Códigos de resposta
- Validação de dados
- **Marcadores**: `@pytest.mark.api`

## 🏷️ Sistema de Marcadores

### Marcadores por Tipo
- `unit` - Testes unitários
- `integration` - Testes de integração
- `e2e` - Testes end-to-end
- `api` - Testes de API

### Marcadores por Funcionalidade
- `smoke` - Testes críticos/rápidos
- `regression` - Testes de regressão
- `crud` - Operações CRUD
- `auth` - Autenticação
- `database` - Operações de banco
- `ui` - Interface do usuário
- `forms` - Formulários
- `validation` - Validações

### Marcadores por Performance
- `slow` - Testes demorados
- `fast` - Testes rápidos

## 🛠️ Fixtures Organizadas

### Fixtures de Banco de Dados
```python
test_database      # Banco temporário para sessão
clean_database     # Banco limpo para cada teste
database_connection # Conexão direta ao banco
database_cursor    # Cursor do banco
empty_database     # Banco completamente vazio
```

### Fixtures de Autenticação
```python
admin_credentials     # Credenciais do admin
guest_credentials     # Credenciais de hóspede
app_client           # Cliente Flask
logged_admin_client  # Cliente com admin logado
logged_guest_client  # Cliente com hóspede logado
```

### Fixtures de Dados
```python
valid_guest_data     # Dados válidos de hóspede
invalid_guest_data   # Dados inválidos
valid_admin_data     # Dados válidos de admin
random_guest_data    # Dados aleatórios (Faker)
multiple_guests_data # Múltiplos hóspedes
edge_case_data      # Casos extremos
sql_injection_data  # Dados para teste de segurança
```

## 🚀 Executando Testes

### Por Categoria
```bash
# Testes unitários
pytest tests/unit -v

# Testes de integração
pytest tests/integration -v

# Testes end-to-end
pytest tests/e2e -v

# Testes de API
pytest tests/api -v
```

### Por Marcador
```bash
# Testes rápidos
pytest -m smoke -v

# Testes de autenticação
pytest -m auth -v

# Testes CRUD
pytest -m crud -v

# Testes sem os lentos
pytest -m "not slow" -v
```

### Combinações
```bash
# Testes unitários rápidos
pytest -m "unit and smoke" -v

# Testes de integração de autenticação
pytest -m "integration and auth" -v

# Todos exceto E2E e lentos
pytest -m "not e2e and not slow" -v
```

### Execução Específica
```bash
# Arquivo específico
pytest tests/unit/test_simple.py -v

# Classe específica
pytest tests/integration/test_auth_integration.py::TestAuthFlow -v

# Teste específico
pytest tests/unit/test_simple.py::test_app_import -v
```

## 📊 Relatórios e Análise

### Relatório HTML
```bash
pytest tests/ --html=reports/relatorio.html --self-contained-html -v
```

### Relatório de Cobertura
```bash
pytest tests/ --cov=src/restel --cov-report=html --cov-report=term-missing
```

### Relatório de Duração
```bash
pytest tests/ --durations=10 -v
```

## 🔧 Configuração Avançada

### Arquivo pytest.ini
O arquivo `config/pytest.ini` contém todas as configurações:
- Marcadores personalizados
- Opções padrão
- Filtros de warnings
- Configuração de logging

### Configuração de Ambiente
```bash
# Executar em modo headless (padrão)
export PYTEST_BROWSER_HEADLESS=true

# Executar com browser visível
export PYTEST_BROWSER_HEADLESS=false

# Configurar timeout
export PYTEST_TIMEOUT=300
```

## 💡 Dicas e Boas Práticas

### Escrevendo Testes
1. **Use marcadores apropriados** para categorizar seus testes
2. **Nomeie testes descritivamente** - `test_admin_can_create_guest`
3. **Use fixtures** em vez de configuração manual
4. **Teste casos felizes E casos de erro**
5. **Mantenha testes independentes** (sem dependências entre eles)

### Organizando Testes
1. **Coloque testes na categoria correta** (unit/integration/e2e/api)
2. **Use classes** para agrupar testes relacionados
3. **Documente** o que cada teste faz
4. **Mantenha dados de teste** nas fixtures apropriadas

### Performance
1. **Use `@pytest.mark.slow`** para testes demorados
2. **Prefira testes unitários** quando possível
3. **Use `scope="session"`** para fixtures caras
4. **Execute testes em paralelo** quando necessário

## 🆘 Solução de Problemas

### Problemas Comuns

#### Erro de Import
```
ModuleNotFoundError: No module named 'app'
```
**Solução**: Verificar se o PYTHONPATH está configurado corretamente

#### Selenium Não Funciona
```
WebDriverException: chrome not reachable
```
**Solução**: 
1. Instalar/atualizar Chrome
2. Reinstalar webdriver-manager
3. Verificar se está em modo headless

#### Banco de Dados Não Encontrado
```
sqlite3.OperationalError: no such table
```
**Solução**: Verificar se as fixtures de banco estão sendo usadas

#### Testes Lentos
**Solução**:
1. Usar marcador `@pytest.mark.slow`
2. Executar apenas testes rápidos: `pytest -m "not slow"`
3. Paralelizar com pytest-xdist

### Debug de Testes
```bash
# Executar com mais detalhes
pytest tests/ -v --tb=long

# Parar no primeiro erro
pytest tests/ -x

# Executar apenas testes que falharam
pytest tests/ --lf

# Mostrar prints
pytest tests/ -s
```

## 📈 Métricas e Qualidade

### Cobertura de Código
- **Meta**: > 80% de cobertura
- **Foco**: Funcionalidades críticas primeiro
- **Exclusões**: Arquivos de configuração

### Categorias de Teste
- **Unit**: 40-50% dos testes
- **Integration**: 30-40% dos testes  
- **E2E**: 10-20% dos testes
- **API**: 10-15% dos testes

### Performance
- **Testes rápidos**: < 1 segundo
- **Testes médios**: 1-10 segundos
- **Testes lentos**: > 10 segundos

## 🔄 Integração Contínua

### GitHub Actions / CI
```yaml
- name: Run Tests
  run: |
    pytest tests/unit tests/integration -v --tb=short
    pytest tests/api -v --tb=short
    # E2E apenas em branch main
```

### Pre-commit Hook
```bash
# Executar testes rápidos antes do commit
pytest -m "smoke" --tb=short
```

---

📞 **Suporte**: Para dúvidas sobre os testes, consulte a documentação ou abra uma issue.

🏢 **SWFactory Consultoria e Sistemas Ltda** - Sistema RESTEL 