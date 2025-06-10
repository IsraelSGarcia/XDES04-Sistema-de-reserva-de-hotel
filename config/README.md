# 📁 Configurações do Projeto

Este diretório contém todos os arquivos de configuração do projeto RESTEL.

## 📋 Arquivos

### **pytest.ini**
Configurações para execução dos testes com pytest.

### **requirements.txt** 
Dependências principais do projeto Flask.

### **requirements-test.txt**
Dependências específicas para testes e desenvolvimento.

### **pyrightconfig.json**
Configurações do analisador de tipos Python (Pyright).

## 🚀 Uso

Para instalar dependências:
```bash
# Dependências principais
pip install -r config/requirements.txt

# Dependências de teste
pip install -r config/requirements-test.txt
```

Para executar testes:
```bash
pytest -c config/pytest.ini
``` 