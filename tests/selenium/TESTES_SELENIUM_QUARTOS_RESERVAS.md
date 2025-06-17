# TESTES SELENIUM IDE - QUARTOS E RESERVAS
## Sistema RESTEL - Hotel Reservation System

### 📋 ÍNDICE
1. [Configuração Inicial](#configuração-inicial)
2. [Testes CRUD Quartos](#testes-crud-quartos)
3. [Testes CRUD Reservas](#testes-crud-reservas)
4. [Testes de Integração](#testes-de-integração)
5. [Testes de Validação](#testes-de-validação)
6. [Cenários de Erro](#cenários-de-erro)

---

## 🔧 CONFIGURAÇÃO INICIAL

### Pré-requisitos
- **URL Base**: `http://localhost:5000`
- **Usuário Admin**: `admin@restel.com` / `admin123`
- **Usuário Hóspede**: `hospede@teste.com` / `123456`
- **Navegador**: Chrome/Firefox
- **Selenium IDE**: Versão mais recente

### Setup do Ambiente
1. Iniciar aplicação Flask: `cd src/restel && python app.py`
2. Verificar banco de dados limpo
3. Criar dados de teste básicos

---

## 🏨 TESTES CRUD QUARTOS

### TC001 - Login Administrador
**Objetivo**: Autenticar como administrador
```
1. Abrir URL: http://localhost:5000/admin/login
2. Inserir email: admin@restel.com
3. Inserir senha: admin123
4. Clicar em "Entrar"
5. Verificar redirecionamento para /admin/painel
6. Verificar presença do texto "Painel Administrativo"
```

### TC002 - Cadastrar Quarto - Cenário Positivo
**Objetivo**: Cadastrar novo quarto com dados válidos
```
1. Navegar para /admin/quartos
2. Clicar em "Novo Quarto"
3. Preencher Número: "101"
4. Selecionar Tipo: "Standard"
5. Preencher Capacidade: "2"
6. Preencher Preço Diária: "150.00"
7. Selecionar Status: "Disponível"
8. Clicar em "Salvar"
9. Verificar mensagem de sucesso
10. Verificar quarto na listagem
```

### TC003 - Cadastrar Quarto - Validação Campos Obrigatórios
**Objetivo**: Verificar validação de campos obrigatórios
```
1. Navegar para /admin/quarto/novo
2. Deixar todos os campos vazios
3. Clicar em "Salvar"
4. Verificar mensagens de erro para cada campo obrigatório
5. Verificar que o formulário não foi submetido
```

### TC004 - Cadastrar Quarto - Número Duplicado
**Objetivo**: Verificar validação de número único
```
1. Navegar para /admin/quarto/novo
2. Preencher Número: "101" (já existente)
3. Preencher demais campos válidos
4. Clicar em "Salvar"
5. Verificar mensagem de erro sobre número duplicado
```

### TC005 - Listar Quartos
**Objetivo**: Verificar listagem de quartos
```
1. Navegar para /admin/quartos
2. Verificar cabeçalhos da tabela
3. Verificar dados dos quartos cadastrados
4. Verificar botões de ação (Editar, Excluir)
5. Verificar paginação (se aplicável)
```

### TC006 - Buscar Quarto por Número
**Objetivo**: Testar funcionalidade de busca
```
1. Navegar para /admin/quartos
2. Inserir "101" no campo de busca
3. Clicar em "Buscar"
4. Verificar que apenas quartos com número "101" aparecem
5. Limpar busca e verificar todos os quartos
```

### TC007 - Filtrar Quartos por Tipo
**Objetivo**: Testar filtro por tipo
```
1. Navegar para /admin/quartos
2. Selecionar "Standard" no filtro de tipo
3. Aplicar filtro
4. Verificar que apenas quartos "Standard" aparecem
5. Testar outros tipos (Luxo, Suíte)
```

### TC008 - Filtrar Quartos por Capacidade
**Objetivo**: Testar filtro por capacidade
```
1. Navegar para /admin/quartos
2. Selecionar "2" no filtro de capacidade
3. Aplicar filtro
4. Verificar que apenas quartos com capacidade 2 aparecem
5. Testar outras capacidades
```

### TC009 - Editar Quarto - Cenário Positivo
**Objetivo**: Editar dados de um quarto existente
```
1. Navegar para /admin/quartos
2. Clicar em "Editar" no quarto 101
3. Alterar Preço Diária para "180.00"
4. Alterar Status para "Manutenção"
5. Clicar em "Salvar"
6. Verificar mensagem de sucesso
7. Verificar alterações na listagem
```

### TC010 - Editar Quarto - Validação
**Objetivo**: Verificar validações na edição
```
1. Navegar para edição do quarto 101
2. Limpar campo "Preço Diária"
3. Tentar salvar
4. Verificar mensagem de erro
5. Inserir valor inválido (texto)
6. Verificar validação
```

### TC011 - Excluir Quarto - Sem Reservas
**Objetivo**: Excluir quarto que não possui reservas
```
1. Navegar para /admin/quartos
2. Clicar em "Excluir" no quarto sem reservas
3. Confirmar exclusão no modal
4. Verificar mensagem de sucesso
5. Verificar que quarto foi removido da listagem
```

### TC012 - Excluir Quarto - Com Reservas
**Objetivo**: Tentar excluir quarto com reservas ativas
```
1. Navegar para /admin/quartos
2. Clicar em "Excluir" no quarto com reservas
3. Verificar mensagem de erro sobre reservas ativas
4. Verificar que quarto não foi excluído
```

---

## 📅 TESTES CRUD RESERVAS

### TC013 - Cadastrar Reserva (Admin) - Cenário Positivo
**Objetivo**: Administrador cadastra nova reserva
```
1. Navegar para /admin/reservas
2. Clicar em "Nova Reserva"
3. Selecionar Hóspede existente
4. Selecionar Quarto disponível
5. Definir Data Check-in: "2024-03-15"
6. Definir Data Check-out: "2024-03-17"
7. Definir Número de Hóspedes: "2"
8. Clicar em "Salvar"
9. Verificar cálculo automático do valor
10. Verificar mensagem de sucesso
```

### TC014 - Cadastrar Reserva - Validação Datas
**Objetivo**: Verificar validação de datas
```
1. Navegar para /admin/reserva/nova
2. Definir Check-out anterior ao Check-in
3. Tentar salvar
4. Verificar mensagem de erro
5. Definir Check-in no passado
6. Verificar validação
```

### TC015 - Cadastrar Reserva - Conflito de Datas
**Objetivo**: Verificar detecção de conflitos
```
1. Navegar para /admin/reserva/nova
2. Selecionar quarto já reservado
3. Definir datas que conflitam com reserva existente
4. Tentar salvar
5. Verificar mensagem de erro sobre conflito
```

### TC016 - Cadastrar Reserva - Capacidade Excedida
**Objetivo**: Verificar validação de capacidade
```
1. Navegar para /admin/reserva/nova
2. Selecionar quarto com capacidade 2
3. Definir número de hóspedes como 4
4. Tentar salvar
5. Verificar mensagem de erro sobre capacidade
```

### TC017 - Listar Reservas (Admin)
**Objetivo**: Verificar listagem administrativa
```
1. Navegar para /admin/reservas
2. Verificar cabeçalhos da tabela
3. Verificar dados das reservas
4. Verificar status das reservas
5. Verificar botões de ação
```

### TC018 - Buscar Reserva por Hóspede
**Objetivo**: Testar busca por nome do hóspede
```
1. Navegar para /admin/reservas
2. Inserir nome do hóspede na busca
3. Aplicar filtro
4. Verificar resultados corretos
```

### TC019 - Filtrar Reservas por Status
**Objetivo**: Testar filtro por status
```
1. Navegar para /admin/reservas
2. Selecionar "Confirmada" no filtro
3. Aplicar filtro
4. Verificar apenas reservas confirmadas
5. Testar outros status
```

### TC020 - Editar Reserva (Admin)
**Objetivo**: Administrador edita reserva existente
```
1. Navegar para /admin/reservas
2. Clicar em "Editar" em uma reserva
3. Alterar datas da reserva
4. Alterar número de hóspedes
5. Salvar alterações
6. Verificar recálculo do valor
7. Verificar mensagem de sucesso
```

### TC021 - Check-in de Reserva
**Objetivo**: Realizar check-in de uma reserva
```
1. Navegar para /admin/reservas
2. Localizar reserva com status "Confirmada"
3. Clicar em "Check-in"
4. Confirmar ação
5. Verificar mudança de status para "Em Andamento"
6. Verificar que quarto ficou "Ocupado"
```

### TC022 - Check-out de Reserva
**Objetivo**: Realizar check-out de uma reserva
```
1. Navegar para /admin/reservas
2. Localizar reserva com status "Em Andamento"
3. Clicar em "Check-out"
4. Confirmar ação
5. Verificar mudança de status para "Finalizada"
6. Verificar que quarto voltou para "Disponível"
```

### TC023 - Cancelar Reserva (Admin)
**Objetivo**: Administrador cancela reserva
```
1. Navegar para /admin/reservas
2. Clicar em "Cancelar" em uma reserva
3. Confirmar cancelamento
4. Verificar mudança de status para "Cancelada"
5. Verificar liberação do quarto
```

---

## 👤 TESTES ÁREA DO HÓSPEDE

### TC024 - Login Hóspede
**Objetivo**: Autenticar como hóspede
```
1. Abrir URL: http://localhost:5000/hospede/login
2. Inserir email: hospede@teste.com
3. Inserir senha: 123456
4. Clicar em "Entrar"
5. Verificar redirecionamento para /hospede/painel
6. Verificar presença do painel do hóspede
```

### TC025 - Nova Reserva (Hóspede)
**Objetivo**: Hóspede cria nova reserva
```
1. Navegar para /hospede/reserva/nova
2. Selecionar quarto disponível
3. Definir datas válidas
4. Definir número de hóspedes
5. Clicar em "Reservar"
6. Verificar cálculo do valor
7. Verificar confirmação da reserva
```

### TC026 - Visualizar Minhas Reservas
**Objetivo**: Hóspede visualiza suas reservas
```
1. Navegar para /hospede/reservas
2. Verificar listagem de reservas do hóspede logado
3. Verificar informações das reservas
4. Verificar botões de ação disponíveis
```

### TC027 - Editar Reserva (Hóspede) - Permitido
**Objetivo**: Hóspede edita reserva dentro do prazo
```
1. Navegar para /hospede/reservas
2. Clicar em "Editar" em reserva futura (>24h)
3. Alterar datas da reserva
4. Salvar alterações
5. Verificar recálculo do valor
6. Verificar mensagem de sucesso
```

### TC028 - Editar Reserva (Hóspede) - Bloqueado
**Objetivo**: Tentar editar reserva fora do prazo
```
1. Navegar para /hospede/reservas
2. Tentar editar reserva com check-in <24h
3. Verificar mensagem de bloqueio
4. Verificar que edição não é permitida
```

### TC029 - Cancelar Reserva (Hóspede) - Permitido
**Objetivo**: Hóspede cancela reserva dentro do prazo
```
1. Navegar para /hospede/reservas
2. Clicar em "Cancelar" em reserva futura (>24h)
3. Confirmar cancelamento
4. Verificar mudança de status
5. Verificar mensagem de confirmação
```

### TC030 - Cancelar Reserva (Hóspede) - Bloqueado
**Objetivo**: Tentar cancelar reserva fora do prazo
```
1. Navegar para /hospede/reservas
2. Tentar cancelar reserva com check-in <24h
3. Verificar mensagem de bloqueio
4. Verificar que cancelamento não é permitido
```

---

## 🔗 TESTES DE INTEGRAÇÃO

### TC031 - Fluxo Completo Reserva
**Objetivo**: Testar fluxo completo de uma reserva
```
1. Admin cadastra novo quarto
2. Hóspede faz login
3. Hóspede cria nova reserva
4. Admin visualiza reserva na listagem
5. Admin realiza check-in
6. Admin realiza check-out
7. Verificar status final da reserva
```

### TC032 - Conflito de Reservas
**Objetivo**: Testar detecção de conflitos
```
1. Criar reserva para quarto X (data A-B)
2. Tentar criar segunda reserva para mesmo quarto (data A-B)
3. Verificar bloqueio da segunda reserva
4. Criar reserva com datas parcialmente sobrepostas
5. Verificar detecção do conflito
```

### TC033 - Atualização de Status do Quarto
**Objetivo**: Verificar sincronização de status
```
1. Verificar quarto como "Disponível"
2. Fazer check-in de reserva
3. Verificar quarto como "Ocupado"
4. Fazer check-out
5. Verificar quarto volta para "Disponível"
```

---

## ⚠️ CENÁRIOS DE ERRO

### TC034 - Acesso Não Autorizado
**Objetivo**: Verificar controle de acesso
```
1. Tentar acessar /admin/quartos sem login
2. Verificar redirecionamento para login
3. Fazer login como hóspede
4. Tentar acessar área administrativa
5. Verificar bloqueio de acesso
```

### TC035 - Dados Inválidos
**Objetivo**: Testar validação de dados
```
1. Inserir caracteres especiais em campos numéricos
2. Inserir valores negativos em preços
3. Inserir datas em formato inválido
4. Verificar tratamento de erros
```

### TC036 - Sessão Expirada
**Objetivo**: Testar comportamento com sessão expirada
```
1. Fazer login
2. Simular expiração de sessão
3. Tentar realizar ação
4. Verificar redirecionamento para login
```

---

## 📊 RELATÓRIO DE EXECUÇÃO

### Estrutura do Relatório
```
- Total de Testes: 36
- Testes Executados: ___
- Testes Passaram: ___
- Testes Falharam: ___
- Taxa de Sucesso: ___%
```

### Classificação por Módulo
```
- CRUD Quartos: 12 testes
- CRUD Reservas: 11 testes  
- Área Hóspede: 7 testes
- Integração: 3 testes
- Cenários de Erro: 3 testes
```

---

## 🔧 COMANDOS SELENIUM IDE

### Comandos Principais Utilizados
- `open` - Abrir URL
- `click` - Clicar em elemento
- `type` - Inserir texto
- `select` - Selecionar opção
- `verifyText` - Verificar texto
- `verifyElementPresent` - Verificar presença de elemento
- `waitForElementVisible` - Aguardar elemento
- `assertAlert` - Verificar alerta

### Seletores Recomendados
- `id=elemento_id` - Por ID
- `name=elemento_name` - Por nome
- `css=.classe` - Por classe CSS
- `xpath=//div[@class='exemplo']` - Por XPath

---

## 📝 OBSERVAÇÕES

1. **Dados de Teste**: Sempre usar dados consistentes
2. **Limpeza**: Limpar dados entre testes quando necessário
3. **Esperas**: Usar waits adequados para elementos dinâmicos
4. **Screenshots**: Capturar evidências em caso de falha
5. **Logs**: Manter logs detalhados da execução

---

**Criado em**: $(date)  
**Versão**: 1.0  
**Sistema**: RESTEL Hotel Reservation System 