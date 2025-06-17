# Dados Únicos para Testes Selenium

## 📋 Visão Geral

Este documento descreve como o sistema de testes Selenium foi configurado para usar **dados únicos e não conflitantes**, garantindo que cada execução seja independente e confiável.

## 🎯 Problema Resolvido

**Antes**: Os testes usavam dados fixos que causavam conflitos:
- Quartos com números repetidos (201, 202)
- Emails genéricos que podiam existir no banco
- Datas passadas ou fixas
- Dados que interferiam entre execuções

**Agora**: Sistema automatizado que garante dados únicos:
- Quartos específicos para cada tipo de teste
- Emails e senhas alinhados com o arquivo de teste
- Datas sempre futuras e válidas
- Limpeza automática entre execuções

## 🏗️ Estrutura dos Dados

### Quartos de Teste
```
101 - Standard (2 pessoas) - R$ 300/dia    # Para testes de reserva
404 - Luxo (3 pessoas) - R$ 600/dia        # Para teste de cadastro válido
5050 - (NÃO CRIADO)                        # Para teste de cadastro inválido
```

### Hóspedes de Teste
```
Nome: fcgvhbjk
Email: dfvsdf@gmail.com
Senha: fgsgfgsg
CPF: 12345678901
Telefone: 11987654321

Nome: Ana Costa
Email: ana.costa@teste.com
Senha: senha123
CPF: 12345678904
Telefone: 11987654324
```

### Datas de Teste
As datas são **sempre calculadas dinamicamente** para serem futuras:
- Check-in hóspede: Data base (hoje + 30 dias)
- Check-out hóspede: Data base + 1 dia
- Check-in admin: Data base + 1 dia
- Check-out admin: Data base + 2 dias

## 🚀 Como Usar

### 1. Preparação Automática
```bash
# Windows
cd tests/selenium
python prepare_test_data.py

# Ou use o script completo
run_tests_with_unique_data.bat
```

### 2. Execução Manual
```bash
# Preparar dados
python prepare_test_data.py

# Executar testes
selenium-side-runner Release\ 01.side
```

## 📊 Mapeamento de Testes

| Teste | Dados Usados | Propósito |
|-------|-------------|-----------|
| TC002 - Cadastrar quarto válido | Quarto 404, Luxo, 3 pessoas, R$ 600 | Teste de cadastro bem-sucedido |
| TC003 - Cadastrar quarto inválido | Quarto 5050 (não existe no banco) | Teste de validação de erro |
| TC005 - Login hóspede | dfvsdf@gmail.com / fgsgfgsg | Autenticação de hóspede |
| TC024 - Nova reserva hóspede | Quarto 101, datas futuras | Reserva pelo hóspede |
| TC026 - Visualizar reservas | dfvsdf@gmail.com | Listagem de reservas |
| TC013 - Admin nova reserva | Ana Costa, Quarto 101 | Reserva pelo admin |
| TC017 - Listar reservas admin | Dados existentes | Gestão administrativa |
| TC034 - Acesso não autorizado | URLs protegidas | Segurança |

## 🔧 Script de Preparação

O script `prepare_test_data.py` executa:

1. **Limpeza**: Remove dados de testes anteriores
2. **Criação de Quartos**: Insere quartos específicos para cada teste
3. **Criação de Hóspedes**: Cria usuários com credenciais corretas
4. **Geração de Datas**: Calcula datas sempre futuras
5. **Validação**: Confirma que todos os dados foram criados

## ⚠️ Notas Importantes

- **Quarto 5050**: Propositalmente NÃO é criado no banco para testar validação de erro
- **Datas**: Sempre calculadas dinamicamente (hoje + X dias)
- **Emails**: Mantidos conforme arquivo de teste para compatibilidade
- **Limpeza**: Automática a cada execução

## 🎨 Benefícios

✅ **Execuções Independentes**: Cada teste roda com dados limpos
✅ **Sem Conflitos**: Números únicos evitam sobreposições
✅ **Datas Válidas**: Sempre futuras, nunca expiram
✅ **Manutenção Fácil**: Script automatizado
✅ **Compatibilidade**: Alinhado com Release 01.side
✅ **Confiabilidade**: Resultados previsíveis

## 🔄 Fluxo de Execução

```
1. prepare_test_data.py
   ↓
2. Limpa dados antigos
   ↓
3. Cria quartos (101, 404)
   ↓
4. Cria hóspedes (dfvsdf@gmail.com, ana.costa@teste.com)
   ↓
5. Gera datas futuras
   ↓
6. Confirma preparação
   ↓
7. Executa testes Selenium
```

## 📞 Suporte

Se encontrar problemas:
1. Verifique se o banco de dados existe
2. Execute o script de preparação novamente
3. Confirme que o Flask está rodando na porta 5000
4. Verifique os logs de execução dos testes 