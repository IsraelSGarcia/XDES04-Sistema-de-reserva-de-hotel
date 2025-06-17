# 🌐 Testes End-to-End (E2E) - Sistema RESTEL

Este diretório contém os testes automatizados end-to-end que simulam interações reais do usuário com o sistema através do navegador.

## 📁 Arquivos de Teste

- **`test_guest_crud.py`** - Testes CRUD para funcionalidades de hóspedes
- **`test_admin_crud.py`** - Testes CRUD para funcionalidades de administradores

## 🖥️ Modos de Execução do Browser

### 🎯 Modo Interativo (Recomendado)
```bash
python -m pytest tests/e2e/test_guest_crud.py -v
```
**O que acontece:** O sistema perguntará se você quer ver o browser ou executar em modo transparente.

### 👁️ Modo Visível
```bash
python -m pytest tests/e2e/test_guest_crud.py --visible -v
```
**O que acontece:** O browser abrirá e você poderá ver os testes sendo executados em tempo real.

### 🥷 Modo Transparente (Headless)
```bash
python -m pytest tests/e2e/test_guest_crud.py --headless -v
```
**O que acontece:** Os testes executam em segundo plano sem interface visual (mais rápido).

## 🚀 Exemplos de Uso

### Executar todos os testes e2e
```bash
# Modo interativo
python -m pytest tests/e2e/ -v

# Modo visível
python -m pytest tests/e2e/ --visible -v

# Modo transparente
python -m pytest tests/e2e/ --headless -v
```

### Executar teste específico
```bash
# Teste de criação de hóspede em modo visível
python -m pytest tests/e2e/test_guest_crud.py::TestGuestCRUD::test_create_guest_valid_data --visible -v

# Teste de login admin em modo transparente
python -m pytest tests/e2e/test_admin_crud.py::TestAdminCRUD::test_admin_login_valid_credentials --headless -v
```

### Executar testes por categoria
```bash
# Apenas testes de criação
python -m pytest tests/e2e/ -k "test_create" --visible -v

# Apenas testes de administrador
python -m pytest tests/e2e/test_admin_crud.py --visible -v

# Apenas testes de hóspede
python -m pytest tests/e2e/test_guest_crud.py --headless -v
```

## 🔧 Opções Úteis do Pytest

| Opção | Descrição |
|-------|-----------|
| `-v` ou `--verbose` | Mostra detalhes dos testes |
| `-s` | Mostra prints durante execução |
| `--tb=short` | Traceback mais curto em erros |
| `--maxfail=1` | Para após primeira falha |
| `-x` | Para na primeira falha |
| `--lf` | Executa apenas testes que falharam na última vez |
| `--ff` | Executa primeiro os testes que falharam |

## 📋 Testes Disponíveis

### 🏨 Testes de Hóspedes (`test_guest_crud.py`)
- ✅ Criar hóspede com dados válidos
- ❌ Criar hóspede com dados inválidos  
- 📋 Listar hóspedes (área admin)
- 🔍 Buscar hóspede
- ✏️ Atualizar dados do hóspede
- 🗑️ Excluir hóspede
- 📝 Validação de formulário
- 🧭 Navegação entre páginas

### 👥 Testes de Administradores (`test_admin_crud.py`)
- 🔐 Login com credenciais válidas/inválidas
- ✅ Criar administrador com dados válidos
- ❌ Criar administrador com dados inválidos
- 📋 Listar administradores
- 🔍 Buscar administrador
- ✏️ Atualizar dados do administrador
- 🗑️ Excluir administrador
- 📝 Validação de formulários
- 🔄 Cancelar edição
- 🧭 Navegação do painel

## 🛠️ Configuração e Troubleshooting

### Pré-requisitos
- Python 3.7+
- Chrome/Chromium instalado
- Dependências: `pip install -r requirements-test.txt`

### Screenshots de Erro
Em caso de falha, screenshots são salvos automaticamente em:
```
tests/screenshots/FAILED_[nome_do_teste].png
```

### Problemas Comuns

**❌ "ChromeDriver not found"**
```bash
pip install webdriver-manager
```

**❌ "Connection refused"**
- Verifique se o servidor Flask está rodando
- Os testes iniciam automaticamente o servidor

**❌ Teste muito lento**
- Use modo `--headless` para execução mais rápida
- Diminua timeouts em `conftest.py` se necessário

**❌ Elemento não encontrado**
- Aumente o `WAIT_TIMEOUT` em `conftest.py`
- Verifique se a página carregou completamente

## 🎯 Dicas de Uso

1. **Para desenvolvimento**: Use `--visible` para ver o que está acontecendo
2. **Para CI/CD**: Use `--headless` para execução automatizada
3. **Para debug**: Use `-s` para ver prints e `-v` para detalhes
4. **Para speed**: Use `--headless` e remova `-v` para execução silenciosa

## 📞 Suporte

Em caso de problemas:
1. Verifique os logs do teste
2. Analise screenshots de erro em `tests/screenshots/`
3. Execute em modo `--visible` para ver o comportamento
4. Consulte a documentação do projeto principal 