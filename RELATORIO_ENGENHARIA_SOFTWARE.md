# Relatório de Engenharia de Software: Sistema RESTEL

## 1. Introdução

Este documento apresenta um relatório técnico sobre o projeto **RESTEL**, um Sistema de Gestão de Reservas de Hotel desenvolvido como parte da disciplina de Engenharia de Software. O sistema foi projetado para a rede de hotéis "Boa Estadia", com o objetivo de modernizar e automatizar seus processos de reserva, oferecendo conveniência aos hóspedes e otimizando a gestão interna.

A plataforma web permite que hóspedes realizem e gerenciem suas reservas online, enquanto a equipe administrativa possui um painel de controle completo para gerenciar quartos, hóspedes, administradores e o fluxo de hospedagem.

## 2. Arquitetura e Tecnologias

O sistema RESTEL é construído como uma aplicação web monolítica, com uma arquitetura cliente-servidor clara.

-   **Backend:**
    -   **Linguagem:** Python
    -   **Framework:** Flask
    -   **Segurança:** Criptografia de senhas com Werkzeug (PBKDF2).
    -   **Servidor:** Servidor de desenvolvimento Werkzeug (para ambiente local).

-   **Frontend:**
    -   **Estrutura:** HTML5, CSS3, JavaScript.
    -   **Framework CSS:** Bootstrap 5 para garantir um design moderno e responsivo.
    -   **Ícones:** Font Awesome.
    -   **Templates:** Jinja2, integrado ao Flask.

-   **Banco de Dados:**
    -   **SGBD:** SQLite, um sistema de banco de dados leve e baseado em arquivo, adequado para desenvolvimento e pequenas aplicações. O banco de dados está localizado em `data/restel.db`.

-   **Testes e Automação:**
    -   **Framework de Testes:** `pytest` para testes unitários e de integração.
    -   **Testes E2E:** Selenium WebDriver para testes de interface do usuário.
    -   **Automação:** Scripts em Python para configuração de ambiente e execução de testes.

## 3. Estrutura do Projeto

O projeto segue uma estrutura de diretórios organizada, que separa claramente as responsabilidades:

```
restel/
├── 📱 src/restel/          # Código-fonte da aplicação principal
│   ├── app.py             # Arquivo principal da aplicação Flask
│   └── templates/         # Templates HTML (Jinja2)
├── 🧪 tests/               # Suíte de testes automatizados
│   ├── unit/              # Testes unitários
│   ├── integration/       # Testes de integração
│   └── e2e/               # Testes end-to-end (Selenium)
├── 🔧 tools/               # Ferramentas de automação para desenvolvedores
│   ├── iniciar.py         # Script de entrada unificado
│   └── setup_dev.py       # Script de configuração do ambiente
├── ⚙️ config/              # Arquivos de configuração
│   ├── requirements.txt   # Dependências do projeto
│   └── pytest.ini         # Configurações do Pytest
├── 💾 data/                # Banco de dados
│   └── restel.db          # Arquivo do banco de dados SQLite
├── 🎨 static/              # Arquivos estáticos (CSS, JS, Imagens)
├── 📚 docs/                # Documentação do projeto
└── 📝 logs/                # Logs da aplicação
```

## 4. Funcionalidades Implementadas

O sistema implementa um conjunto abrangente de funcionalidades, alinhadas com o `Documento de Requisitos`.

### 4.1. Funcionalidades para Hóspedes

-   **[RF01] Cadastro de Hóspedes:** Permite que novos usuários se cadastrem na plataforma.
-   **Login/Logout:** Autenticação para acesso ao painel do hóspede.
-   **Painel do Hóspede:** Área pessoal para gerenciamento de dados e reservas.
-   **[RF14] Nova Reserva:** Interface para buscar quartos disponíveis e criar uma nova reserva.
-   **Minhas Reservas:** Consulta do histórico de reservas.
-   **[RF16] Cancelamento de Reserva:** Possibilidade de cancelar reservas ativas, respeitando as regras de negócio.
-   **Edição de Reserva:** Alteração de detalhes de uma reserva existente.
-   **[RF20] Contato com o hotel:** Formulário que permite aos visitantes enviar mensagens para a administração do hotel.

### 4.2. Funcionalidades para Administradores

O painel administrativo é acessível apenas por usuários autenticados e possui controle de acesso baseado em perfis (`Master` e `Padrão`).

-   **[RF06] Login/Logout de Administrador:** Acesso seguro ao painel de controle.
-   **Dashboard:** Visão geral com estatísticas rápidas do sistema.
-   **[RF01-RF04] Gerenciamento de Hóspedes:** CRUD completo para os cadastros de hóspedes.
-   **[RF05-RF09] Gerenciamento de Administradores:** O perfil `Master` pode realizar o CRUD de outros usuários administradores.
-   **[RF10-RF13] Gerenciamento de Quartos:** CRUD completo para os quartos do hotel, incluindo a gestão de status (Disponível, Manutenção).
-   **Gerenciamento de Reservas:** Visualização de todas as reservas do sistema, com filtros e opções para editar, cancelar, e processar check-in/check-out.
-   **Relatórios:** Geração de relatórios, como a lista de reservas por período.
-   **Notificações:** Sistema de notificações internas e Push Notifications para eventos importantes (ex: check-ins próximos).
-   **Gerenciamento de Contatos:** Interface para visualizar e gerenciar as mensagens enviadas através do formulário de contato.

## 5. Sistema de Testes

O projeto demonstra uma forte cultura de qualidade através de uma suíte de testes bem estruturada.

-   **Executor de Testes Interativo:** O script `tools/test_runner.py` oferece uma interface em português para executar diferentes tipos de testes (unitários, integração, CRUD, etc.) e gerar relatórios.
-   **Cobertura:** Os testes cobrem rotas da API, lógica de negócios e as operações de CRUD para as principais entidades do sistema.
-   **Relatórios de Teste:** Capacidade de gerar relatórios em HTML com `pytest-html` para fácil visualização dos resultados.
-   **Testes de Interface (E2E):** Utilização do Selenium para simular a interação do usuário com a aplicação, validando os fluxos completos.

## 6. Recursos Adicionais

Além dos requisitos funcionais básicos, o sistema inclui vários recursos que melhoram sua robustez e usabilidade.

-   **Validação de Dados:** Validações no backend e frontend (ex: formato de CPF e e-mail) para garantir a integridade dos dados.
-   **Interface Responsiva:** O uso do Bootstrap 5 torna a interface adaptável a diferentes tamanhos de tela (desktop, tablet e mobile).

## 7. Conclusão

O projeto RESTEL é uma aplicação web funcional e bem estruturada que atende com sucesso aos requisitos definidos. A clara separação de responsabilidades na estrutura de arquivos, a pilha de tecnologia moderna, e a abrangente suíte de testes são pontos fortes que demonstram a aplicação de boas práticas de Engenharia de Software.

O sistema fornece uma base sólida que pode ser estendida no futuro com novas funcionalidades, como integração com sistemas de pagamento, módulos de governança ou programas de fidelidade. 