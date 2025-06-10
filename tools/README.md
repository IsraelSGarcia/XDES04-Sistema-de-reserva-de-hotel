# 🔧 Ferramentas de Desenvolvimento - RESTEL

Esta pasta contém as ferramentas essenciais para desenvolvimento e manutenção do sistema RESTEL.

## 🚀 Como Usar - Guia Rápido

### 1️⃣ **Primeira Vez? Configure o Ambiente**
```bash
python tools/setup_dev.py
```
☝️ Execute isso primeiro para configurar tudo automaticamente!

### 2️⃣ **Executar Testes**
```bash
python tools/test_runner.py
```
☝️ Interface interativa para rodar todos os tipos de teste!

### 3️⃣ **Script Principal (Tudo em Um)**
```bash
python tools/iniciar.py
```
☝️ Menu principal com todas as opções disponíveis!

---

## 📋 Ferramentas Detalhadas

### 🛠️ `setup_dev.py` - Configuração Automática

**O que faz:** Prepara todo o ambiente de desenvolvimento automaticamente

**Quando usar:** 
- ✅ Primeira instalação do projeto
- ✅ Após clonar o repositório
- ✅ Quando há problemas com dependências
- ✅ Para resetar o ambiente

**Como executar:**
```bash
# Na raiz do projeto
python tools/setup_dev.py
```

**O que acontece quando você executa:**
1. 🔍 Verifica versão do Python (3.7+)
2. 📦 Instala dependências automaticamente
3. 📁 Cria estrutura de diretórios necessária
4. 🗄️ Inicializa banco de dados SQLite
5. 📝 Cria arquivo .gitignore
6. 🧪 Executa testes iniciais para verificar funcionamento
7. ✅ Confirma se tudo está funcionando

**Saída esperada:**
```
🚀 CONFIGURAÇÃO DO AMBIENTE DE DESENVOLVIMENTO
✅ Python 3.x detectado
✅ Dependências instaladas
✅ Estrutura criada
✅ Banco inicializado  
✅ Testes passaram
🎉 Ambiente configurado com sucesso!
```

---

### 🧪 `test_runner.py` - Executor de Testes

**O que faz:** Interface interativa para executar diferentes tipos de testes

**Quando usar:**
- ✅ Antes de fazer commit no código
- ✅ Após fazer mudanças no sistema
- ✅ Para verificar se tudo está funcionando
- ✅ Para gerar relatórios de teste

**Como executar:**
```bash
# Na raiz do projeto
python tools/test_runner.py
```

**Menu interativo disponível:**
```
🧪 EXECUTOR DE TESTES - SISTEMA RESTEL

1. 🚀 Executar TODOS os testes
2. 🔬 Apenas testes unitários
3. 🔗 Testes de integração  
4. 👤 Testes CRUD de hóspedes
5. 🔐 Testes CRUD de administradores
6. 🌐 Testes de rotas
7. 📊 Gerar relatório HTML
8. 🧹 Limpar cache de testes
9. ❓ Ajuda e informações
0. 🚪 Sair

Escolha uma opção:
```

**Opções mais úteis:**
- **Opção 1:** Para verificação completa
- **Opção 7:** Para relatórios detalhados com HTML
- **Opção 8:** Quando há problemas com cache

---

### 🎯 `iniciar.py` - Script Principal

**O que faz:** Menu unificado com todas as funcionalidades do projeto

**Quando usar:**
- ✅ Ponto de entrada principal
- ✅ Quando não sabe qual ferramenta usar
- ✅ Para acessar todas as funcionalidades

**Como executar:**
```bash
# Na raiz do projeto  
python tools/iniciar.py
```

**Menu principal:**
```
🏨 SISTEMA RESTEL - MENU PRINCIPAL

1. ⚙️ Configurar ambiente de desenvolvimento
2. 🧪 Executar testes interativos
3. 🚀 Iniciar aplicação web
4. 📊 Status do projeto
5. 📚 Documentação
6. 🔧 Ferramentas de desenvolvimento
0. 🚪 Sair

Escolha uma opção:
```

---

## 🛠️ Casos de Uso Comuns

### 🔰 **Sou novo no projeto**
```bash
# 1. Configure o ambiente
python tools/setup_dev.py

# 2. Execute os testes para verificar
python tools/test_runner.py
# Escolha opção 1 (todos os testes)

# 3. Inicie a aplicação
python tools/iniciar.py  
# Escolha opção 3 (iniciar web)
```

### 🔧 **Desenvolvendo novas funcionalidades**
```bash
# 1. Teste antes de começar
python tools/test_runner.py

# 2. [Faça suas alterações...]

# 3. Teste novamente
python tools/test_runner.py
# Foque nos testes relacionados à sua mudança

# 4. Gere relatório final
python tools/test_runner.py
# Escolha opção 7 (relatório HTML)
```

### 🐛 **Resolvendo problemas**
```bash
# 1. Limpe o cache
python tools/test_runner.py
# Escolha opção 8 (limpar cache)

# 2. Reconfigure o ambiente
python tools/setup_dev.py

# 3. Teste novamente
python tools/test_runner.py
# Escolha opção 1 (todos os testes)
```

### 📊 **Verificação rápida**
```bash
# Script principal para overview
python tools/iniciar.py
# Escolha opção 4 (status do projeto)
```

---

## 🔧 Solução de Problemas

### ❌ **Erro: "Módulo não encontrado"**
```bash
# Reconfigure as dependências
python tools/setup_dev.py
```

### ❌ **Testes falhando**
```bash
# Limpe o cache primeiro
python tools/test_runner.py  # Opção 8
# Depois execute os testes novamente
```

### ❌ **Banco de dados com problema**
```bash
# Reinicialize o ambiente completo
python tools/setup_dev.py
```

---

## 📚 Arquivos de Configuração

Todas as configurações agora estão na pasta `../config/`:
- `requirements.txt` - Dependências principais
- `requirements-test.txt` - Dependências de teste
- `pytest.ini` - Configuração de testes
- `pyrightconfig.json` - Configuração de tipos

---

## 🎯 Próximos Passos

1. **Execute setup:** `python tools/setup_dev.py`
2. **Teste tudo:** `python tools/test_runner.py` (opção 1)
3. **Inicie a aplicação:** `python tools/iniciar.py` (opção 3)
4. **Acesse:** http://localhost:5000

---

**💡 Dica:** Use sempre `python tools/iniciar.py` quando estiver em dúvida - ele te guiará para a ferramenta certa! 