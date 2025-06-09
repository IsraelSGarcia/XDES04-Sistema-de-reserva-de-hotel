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

### Instalação

1. **Clone ou baixe o projeto**
   ```bash
   # Se usando git
   git clone https://github.com/IsraelSGarcia/XDES04-Sistema-de-reserva-de-hotel
   cd XDES04-Sistema-de-reserva-de-hotel
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**
   ```bash
   python app.py
   ```

4. **Acesse no navegador**
   ```
   http://localhost:5000
   ```

## 🧪 Testes Automatizados com Selenium IDE

Este projeto inclui um conjunto de testes automatizados para garantir a qualidade e o funcionamento das principais funcionalidades. Utilizamos o Selenium IDE, uma ferramenta de gravação e reprodução de testes no navegador.

### Pré-requisitos
- Um navegador compatível (Google Chrome ou Mozilla Firefox).
- A extensão **Selenium IDE** instalada no seu navegador.
  - [Link para Chrome](https://chrome.google.com/webstore/detail/selenium-ide/mooikfkahbdckldjjndioackbalphokd)
  - [Link para Firefox](https://addons.mozilla.org/en-US/firefox/addon/selenium-ide/)

### Como Executar os Testes

1. **Inicie a aplicação localmente**, conforme as instruções da seção "Como Executar".
   ```bash
   flask run
   ```

2. **Abra o Selenium IDE** no seu navegador.

3. Clique em **"Open an existing project"** e selecione o arquivo `restel_tests.side` que está na raiz deste projeto.

4. Na barra lateral esquerda, selecione a suíte de testes que deseja executar (por exemplo, "Default Suite").

5. Clique no botão **"Run all tests in suite"** para iniciar a execução.

O Selenium IDE irá abrir uma nova janela do navegador e executar automaticamente todos os passos definidos no teste, como preencher formulários, clicar em botões e verificar se os resultados estão corretos.

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

## 🔮 Funcionalidades Futuras

Para expansão do sistema, podem ser implementadas:
- Gerenciamento de quartos
- Sistema de reservas
- Check-in/Check-out
- Relatórios
- Notificações por email
- Histórico de reservas

## 📞 Informações do Projeto

- **Cliente:** Hotel Boa Estadia
- **Desenvolvedor:** SWFactory Consultoria e Sistemas Ltda
- **Versão:** 1.0

## 🐛 Suporte

Em caso de problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme que o Python 3.7+ está sendo usado
3. Certifique-se de que a porta 5000 está disponível
4. O banco SQLite será criado automaticamente na primeira execução

---