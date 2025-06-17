# COMO EXECUTAR TESTES SELENIUM IDE
## Sistema RESTEL - Guia de Execução

### 📥 INSTALAÇÃO E CONFIGURAÇÃO

#### 1. Instalar Selenium IDE
```bash
# Opção 1: Extensão do Chrome
1. Abrir Chrome Web Store
2. Buscar "Selenium IDE"
3. Instalar extensão oficial da Selenium

# Opção 2: Extensão do Firefox
1. Abrir Firefox Add-ons
2. Buscar "Selenium IDE"
3. Instalar extensão oficial
```

#### 2. Preparar Ambiente de Teste
```bash
# 1. Navegar para o diretório do projeto
cd C:/Users/Israel/Desktop/ReservaHotel/restel

# 2. Iniciar aplicação Flask
cd src/restel
python app.py

# 3. Verificar se aplicação está rodando
# Abrir navegador em: http://localhost:5000
```

#### ⚠️ IMPORTANTE: Preparar Dados Únicos
```bash
# EXECUTAR ANTES DOS TESTES para evitar conflitos!
cd tests/selenium
python prepare_test_data.py

# OU usar o script automatizado:
run_tests_with_unique_data.bat
```

### 📂 ARQUIVOS DE TESTE

#### Estrutura dos Arquivos
```
tests/selenium/
├── TESTES_SELENIUM_QUARTOS_RESERVAS.md  # Lista completa de casos de teste
├── restel_selenium_tests.side           # Arquivo importável do Selenium IDE
└── COMO_EXECUTAR_TESTES.md             # Este arquivo
```

### 🚀 EXECUTANDO OS TESTES

#### Método 1: Importar Arquivo .side
```
1. Abrir Selenium IDE (extensão do navegador)
2. Clicar em "Open an existing project"
3. Selecionar arquivo: tests/selenium/restel_selenium_tests.side
4. Projeto será carregado com todos os testes
```

#### Método 2: Criar Testes Manualmente
```
1. Abrir Selenium IDE
2. Criar novo projeto: "RESTEL Tests"
3. Definir Base URL: http://localhost:5000
4. Seguir casos de teste do arquivo TESTES_SELENIUM_QUARTOS_RESERVAS.md
```

### 🎯 EXECUTANDO SUITES DE TESTE

#### Suite Completa (Recomendado)
```
1. No Selenium IDE, selecionar "Suite Completa"
2. Clicar em "Run all tests in suite"
3. Aguardar execução completa (~10-15 minutos)
4. Verificar relatório de resultados
```

#### Suites Específicas

**Suite CRUD Quartos**
```
Testes incluídos:
- TC001: Login Administrador
- TC002: Cadastrar Quarto Positivo
- TC003: Validação Campos Obrigatórios
- TC005: Listar Quartos
- TC006: Buscar Quarto por Número

Tempo estimado: 5 minutos
```

**Suite Reservas Admin**
```
Testes incluídos:
- TC001: Login Administrador
- TC013: Admin Nova Reserva
- TC017: Listar Reservas Admin

Tempo estimado: 3 minutos
```

**Suite Área Hóspede**
```
Testes incluídos:
- TC024: Login Hóspede
- TC025: Nova Reserva Hóspede
- TC026: Visualizar Minhas Reservas

Tempo estimado: 4 minutos
```

**Suite Segurança**
```
Testes incluídos:
- TC034: Acesso Não Autorizado

Tempo estimado: 1 minuto
```

### 🔧 CONFIGURAÇÕES IMPORTANTES

#### Dados de Teste Padrão
```
Administrador:
- Email: admin@restel.com
- Senha: admin123

Hóspede:
- Email: hospede@teste.com
- Senha: 123456

Dados Únicos de Teste (criados automaticamente):
- Quartos: 201-206 (diferentes tipos)
- Hóspedes: emails @teste.com
- Datas: sempre futuras e válidas
```

#### Configurações do Selenium IDE
```
Base URL: http://localhost:5000
Timeout: 10000ms (10 segundos)
Speed: Medium (recomendado)
```

### 📋 PREPARAÇÃO DOS DADOS

#### Antes de Executar os Testes
```sql
-- 1. Limpar dados de teste (opcional)
DELETE FROM reservas WHERE hospede_id IN (SELECT id FROM hospedes WHERE email LIKE '%teste%');
DELETE FROM quartos WHERE numero LIKE '1%';

-- 2. Criar dados básicos necessários
-- (Os testes criarão os dados conforme necessário)
```

#### Dados Criados pelos Testes
```
Quartos:
- Número: 101, Tipo: Standard, Capacidade: 2, Preço: R$ 150,00

Reservas:
- Diversas reservas criadas durante os testes
- Check-ins e check-outs de exemplo
```

### 🏃‍♂️ EXECUÇÃO PASSO A PASSO

#### 1. Preparação (5 minutos)
```bash
# Terminal 1: Iniciar aplicação
cd src/restel
python app.py

# Verificar no navegador se está funcionando
# http://localhost:5000
```

#### 2. Importar Testes (2 minutos)
```
1. Abrir Selenium IDE
2. File → Open → Selecionar restel_selenium_tests.side
3. Verificar se todos os testes foram carregados
```

#### 3. Executar Suite Completa (15 minutos)
```
1. Selecionar "Suite Completa"
2. Clicar em "Run all tests in suite"
3. Monitorar execução
4. Anotar resultados
```

#### 4. Análise de Resultados (5 minutos)
```
1. Verificar testes que passaram/falharam
2. Analisar logs de erro
3. Fazer screenshots de falhas
4. Documentar problemas encontrados
```

### 📊 INTERPRETANDO RESULTADOS

#### Status dos Testes
```
✅ PASSED: Teste executado com sucesso
❌ FAILED: Teste falhou - verificar logs
⏸️ SKIPPED: Teste pulado por dependência
🔄 RUNNING: Teste em execução
```

#### Tipos de Falhas Comuns
```
1. Element not found: Elemento não encontrado na página
   - Verificar se página carregou completamente
   - Verificar seletores CSS/XPath

2. Timeout: Tempo limite excedido
   - Aumentar timeout para elementos lentos
   - Adicionar waits explícitos

3. Assertion failed: Verificação falhou
   - Verificar se dados esperados estão corretos
   - Verificar se aplicação está funcionando
```

### 🔍 DEBUGGING

#### Verificações Essenciais
```
1. Aplicação Flask está rodando?
   curl http://localhost:5000

2. Banco de dados está acessível?
   - Verificar arquivo data/restel.db

3. Dados de login estão corretos?
   - admin@restel.com / admin123
   - hospede@teste.com / 123456

4. Navegador suporta todos os recursos?
   - JavaScript habilitado
   - Cookies habilitados
```

#### Logs Úteis
```
# Terminal da aplicação Flask
- Verificar requests HTTP
- Verificar erros de servidor

# Console do navegador (F12)
- Verificar erros JavaScript
- Verificar requests AJAX
```

### 📈 RELATÓRIOS

#### Estrutura do Relatório Final
```
RELATÓRIO DE EXECUÇÃO - TESTES SELENIUM IDE
===========================================

Data/Hora: ___________
Ambiente: http://localhost:5000
Navegador: Chrome/Firefox ___

RESUMO GERAL:
- Total de Testes: 11
- Executados: ___
- Passou: ___
- Falhou: ___
- Taxa de Sucesso: ___%

DETALHAMENTO POR SUITE:
- Suite CRUD Quartos: ___/5
- Suite Reservas Admin: ___/3  
- Suite Área Hóspede: ___/3
- Suite Segurança: ___/1

FALHAS IDENTIFICADAS:
1. _________________
2. _________________
3. _________________

OBSERVAÇÕES:
_________________________
```

### 🛠️ MANUTENÇÃO DOS TESTES

#### Atualizando Testes
```
1. Modificar arquivo .side conforme necessário
2. Testar alterações individualmente
3. Executar suite completa para validar
4. Atualizar documentação se necessário
```

#### Adicionando Novos Testes
```
1. Definir caso de teste no arquivo .md
2. Implementar no Selenium IDE
3. Adicionar à suite apropriada
4. Testar isoladamente e em conjunto
```

### 🎯 MELHORES PRÁTICAS

#### Durante a Execução
```
1. Sempre executar com aplicação limpa
2. Não interagir com navegador durante testes
3. Monitorar logs da aplicação
4. Fazer backup dos dados antes de testar
```

#### Análise de Resultados
```
1. Documentar todas as falhas
2. Categorizar tipos de problemas
3. Priorizar correções críticas
4. Manter histórico de execuções
```

### 📞 SUPORTE

#### Em Caso de Problemas
```
1. Verificar se aplicação está rodando
2. Verificar dados de login
3. Limpar cache do navegador
4. Reiniciar Selenium IDE
5. Verificar logs da aplicação
```

#### Recursos Adicionais
```
- Documentação Selenium IDE: https://www.selenium.dev/selenium-ide/
- Guia de Seletores: https://selenium-python.readthedocs.io/locating-elements.html
- Comandos Selenium: https://www.selenium.dev/selenium-ide/docs/en/api/commands
```

---

**Última Atualização**: Dezembro 2024  
**Versão**: 1.0  
**Autor**: Sistema RESTEL 