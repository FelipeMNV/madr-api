# 📚 MADR API

API REST para gerenciamento de um acervo digital de romances, desenvolvida com **Python, FastAPI e PostgreSQL**.

O MADR permite gerenciar contas, autenticação e registros literários, incluindo livros e romancistas. O projeto utiliza SQLAlchemy assíncrono para persistência de dados, autenticação JWT e testes automatizados para validar as principais funcionalidades.

> 🚧 **Status:** Em desenvolvimento — backend em construção.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Tech Stack](#-tech-stack)
- [Arquitetura do Projeto](#-arquitetura-do-projeto)
- [Decisões Técnicas](#-decisões-técnicas)
- [Modelo de Dados](#-modelo-de-dados)
- [Funcionalidades](#-funcionalidades)
- [Como Executar](#-como-executar)
- [Testes e Qualidade](#-testes-e-qualidade)
- [Roadmap](#-roadmap)
- [Origem e Evolução](#-origem-e-evolução)

---

## 🔭 Visão Geral

O MADR (Meu Acervo Digital de Romances) é um projeto de backend voltado à organização de obras literárias e seus respectivos romancistas.

A aplicação foi estruturada para trabalhar com três entidades principais:

- **Usuários:** cadastro, autenticação e gerenciamento de contas.
- **Romancistas:** cadastro e gerenciamento de autores.
- **Livros:** gerenciamento das obras e associação com seus romancistas.

A API utiliza comunicação HTTP com respostas em JSON e disponibiliza documentação interativa por meio do Swagger UI.

O desenvolvimento é realizado de forma incremental, com implementação e testes das funcionalidades a cada etapa.

---

## 🧰 Tech Stack

| Categoria | Tecnologia | Finalidade |
|---|---|---|
| Linguagem | Python 3.14 | Desenvolvimento da aplicação |
| Framework | FastAPI | Construção da API REST |
| Validação | Pydantic v2 | Validação e serialização de dados |
| ORM | SQLAlchemy Async | Persistência e consultas assíncronas |
| Banco de dados | PostgreSQL 17 | Armazenamento relacional |
| Driver | Psycopg 3 | Comunicação com PostgreSQL |
| Migrações | Alembic | Versionamento do esquema do banco |
| Autenticação | PyJWT | Geração e validação de tokens JWT |
| Senhas | pwdlib + Argon2 | Hash e verificação de senhas |
| Containerização | Docker Compose | Ambiente local do banco |
| Gerenciamento | Poetry | Dependências e ambiente Python |
| Automação | Taskipy | Execução de tarefas |
| Testes | Pytest + pytest-asyncio | Testes automatizados |
| Integração | Testcontainers | PostgreSQL isolado para testes |
| Dados de teste | Factory Boy | Criação de objetos para testes |
| Tempo simulado | Freezegun | Testes de expiração JWT |
| Qualidade | Ruff | Lint e formatação |

---

## 🏗 Arquitetura do Projeto

A API utiliza uma estrutura organizada por responsabilidades, separando rotas, schemas, modelos, configurações e testes.

```text
madr-api/
├── migrations/                 # Migrações do banco de dados
├── src/
│   └── madr_api/
│       ├── routers/
│       │   ├── auth.py         # Login e renovação de tokens
│       │   ├── users.py        # Gerenciamento de contas
│       │   └── romancistas.py  # Cadastro de romancistas
│       ├── app.py              # Inicialização do FastAPI
│       ├── database.py         # Engine e sessões assíncronas
│       ├── models.py           # Modelos SQLAlchemy
│       ├── schemas.py          # Schemas Pydantic
│       ├── security.py         # JWT, senhas e autenticação
│       └── settings.py         # Configurações da aplicação
├── tests/
│   ├── conftest.py             # Fixtures compartilhadas
│   ├── test_auth.py
│   ├── test_users.py
│   └── test_romancistas.py
├── alembic.ini
├── compose.yaml
├── pyproject.toml
└── README.md
```

A aplicação utiliza injeção de dependências do FastAPI para fornecer sessões de banco de dados e identificar usuários autenticados.

As rotas HTTP recebem dados por meio de schemas Pydantic e utilizam modelos SQLAlchemy para operações no PostgreSQL.

---

## 🧠 Decisões Técnicas

### Autenticação e autorização

A autenticação utiliza **JSON Web Tokens (JWT)**.

Após validar as credenciais, o sistema gera um access token contendo a identificação do usuário e a data de expiração.

As rotas protegidas utilizam `OAuth2PasswordBearer` e uma dependência de autenticação que verifica o JWT e consulta o usuário no banco.

A autorização é aplicada nos endpoints que modificam contas, impedindo que um usuário altere ou exclua registros de outra conta.

As senhas são armazenadas utilizando hash com Argon2, sem persistência em texto puro.

### Persistência assíncrona

A comunicação com o PostgreSQL utiliza o `AsyncSession` do SQLAlchemy.

As operações de escrita são confirmadas por transações, com `commit()` para persistência e `rollback()` para recuperação de operações que falharam.

As alterações na estrutura do banco são versionadas com Alembic.

### Validação e tratamento de erros

Os dados recebidos pela API são validados com Pydantic.

O sistema utiliza códigos HTTP apropriados, incluindo:

| Código | Significado |
|---|---|
| `200 OK` | Operação concluída |
| `201 Created` | Registro criado |
| `401 Unauthorized` | Falha de autenticação |
| `403 Forbidden` | Operação não autorizada |
| `409 Conflict` | Conflito com registro existente |
| `422 Unprocessable Entity` | Dados inválidos |

No cadastro de romancistas, os nomes são normalizados para remover espaços excedentes e padronizar letras minúsculas. Nomes vazios são rejeitados por validação.

### Testes automatizados

Os testes verificam tanto as respostas HTTP quanto os comportamentos da aplicação.

O ambiente de testes utiliza Pytest, fixtures reutilizáveis e PostgreSQL em containers, permitindo verificar operações reais de persistência.

O Freezegun é utilizado para simular a passagem do tempo e testar tokens expirados sem precisar aguardar sua expiração real.

---

## 🗃 Modelo de Dados

O MADR possui três entidades principais:

| Entidade | Campos principais | Relacionamento |
|---|---|---|
| User | ID, username, email, password | Gerenciamento de contas |
| Romancista | ID, nome | Possui vários livros |
| Livro | ID, título, ano, romancista_id | Pertence a um romancista |

O relacionamento entre livros e romancistas é de **um para muitos (1:N)**.

Um romancista pode possuir várias obras cadastradas, enquanto cada livro está associado a um romancista.

---

## ⚙️ Funcionalidades

### Implementadas

**Contas e autenticação**
- Cadastro de usuários.
- Listagem de usuários autenticados.
- Login com JWT.
- Atualização da própria conta.
- Exclusão da própria conta.
- Renovação de access tokens.
- Proteção de endpoints e validação de permissões.

**Romancistas**
- Cadastro de romancistas.
- Normalização de nomes.
- Validação de campos obrigatórios.
- Tratamento de nomes duplicados.

**Infraestrutura**
- PostgreSQL com Docker Compose.
- Migrações utilizando Alembic.
- Testes automatizados e análise de cobertura.
- Lint e formatação com Ruff.

### Em desenvolvimento

- Listagem e busca de romancistas.
- Atualização e exclusão de romancistas.
- CRUD de livros.
- Filtros e paginação do acervo.
- Integração completa dos relacionamentos nos endpoints.

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.14
- Poetry
- Docker e Docker Compose
- Git

### 1. Clonar o repositório

```bash
git clone https://github.com/FelipeMNV/madr-api.git
cd madr-api
```

### 2. Instalar as dependências

```bash
poetry install
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
POSTGRES_USER=madr
POSTGRES_PASSWORD=senha_local
POSTGRES_DB=madr

DATABASE_URL=postgresql+psycopg://madr:senha_local@localhost:5433/madr

SECRET_KEY=substitua_por_uma_chave_aleatoria_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Os valores são exemplos para desenvolvimento local. As credenciais devem corresponder às utilizadas no PostgreSQL.

**Não adicione o arquivo `.env` ao controle de versão.**

### 4. Iniciar o PostgreSQL

```bash
docker compose up -d
```

O banco será disponibilizado localmente na porta `5433`.

### 5. Executar as migrações

```bash
poetry run alembic upgrade head
```

### 6. Iniciar a API

```bash
poetry run task run
```

A API estará disponível em:

`http://127.0.0.1:8000`

Documentação interativa:

`http://127.0.0.1:8000/docs`

---

## 🧪 Testes e Qualidade

### Executar os testes

```bash
poetry run task test
```

A tarefa executa as verificações de lint, roda os testes automatizados e gera o relatório HTML de cobertura.

### Executar somente o lint

```bash
poetry run task lint
```

### Formatar o código

```bash
poetry run task format
```

### Executar um arquivo específico de testes

```bash
poetry run pytest tests/test_romancistas.py -vv
```

O relatório de cobertura pode ser visualizado em `htmlcov/index.html` após sua geração.

Os testes de integração precisam de um ambiente Docker funcional para iniciar o PostgreSQL de testes.

---

## 🗺 Roadmap

| Etapa | Descrição | Status |
|---|---|---|
| 01 | Modelagem das entidades e relacionamentos | ✅ Concluído |
| 02 | PostgreSQL, Docker e Alembic | ✅ Concluído |
| 03 | Cadastro e autenticação de usuários | ✅ Concluído |
| 04 | Atualização, exclusão e renovação JWT | ✅ Concluído |
| 05 | Cadastro de romancistas | ✅ Concluído |
| 06 | CRUD completo de romancistas | 🔄 Em desenvolvimento |
| 07 | CRUD de livros e relacionamentos | ⏳ Planejado |
| 08 | Filtros, paginação e revisão da API | ⏳ Planejado |
| 09 | Documentação e finalização | ⏳ Planejado |
| 10 | Interface web integrada à API | 💡 Evolução futura |

---

## 📖 Origem e Evolução

O MADR utiliza como ponto de partida o desafio final do curso [FastAPI do Zero](https://fastapidozero.dunossauro.com/), do Dunossauro.

O projeto está sendo desenvolvido com foco na aplicação prática de conceitos de desenvolvimento backend, persistência relacional, autenticação e testes automatizados.

Após a conclusão da API, a proposta é evoluir o MADR para uma aplicação Full Stack com interface própria, utilizando React e TypeScript.

A ideia é transformar o acervo em uma plataforma visual de exploração literária, permitindo navegar por obras, conhecer seus romancistas e gerenciar os registros por meio de uma interface web.

---

## 👨‍💻 Autor

**Felipe Vieira**

Estudante de Engenharia de Software, com foco em desenvolvimento de software.

[GitHub](https://github.com/FelipeMNV) · [LinkedIn](https://www.linkedin.com/in/felipe-vieira-578311242/)
