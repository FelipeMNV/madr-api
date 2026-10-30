# MADR API

API REST desenvolvida com FastAPI para gerenciamento de contas, romancistas e livros.

O projeto faz parte do desafio final do curso **FastAPI do Zero**, do Dunossauro. O objetivo é construir uma aplicação com autenticação JWT, persistência em PostgreSQL, relacionamentos entre entidades e testes automatizados.

O desenvolvimento está sendo feito por etapas, com foco em aplicar os conceitos de backend e boas práticas de desenvolvimento.

## Tecnologias

- Python 3.14
- FastAPI e Pydantic
- SQLAlchemy assíncrono e PostgreSQL
- Alembic para migrações
- Docker Compose
- PyJWT e pwdlib (Argon2)
- Pytest, Testcontainers e Factory Boy
- Ruff, Poetry e Taskipy

## Funcionalidades

**Implementadas**
- Cadastro e listagem de usuários
- Autenticação com JWT
- Atualização e exclusão de contas
- Renovação de tokens
- Cadastro de romancistas com validação e normalização de nomes
- Tratamento de erros de autenticação e conflitos de registros
- Testes automatizados

**Em desenvolvimento**
- Listagem, consulta, atualização e exclusão de romancistas
- CRUD de livros
- Filtros e paginação para o acervo

## Executando localmente

É necessário ter Python 3.14, Poetry e Docker instalados.

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/FelipeMNV/madr-api.git
cd madr-api
poetry install
```

Crie um arquivo `.env` na raiz do projeto com as configurações necessárias:

```env
POSTGRES_USER=madr
POSTGRES_PASSWORD=defina_uma_senha
POSTGRES_DB=madr

DATABASE_URL=postgresql+psycopg://madr:defina_uma_senha@localhost:5433/madr
SECRET_KEY=substitua_por_uma_chave_aleatoria_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Os valores acima são exemplos. A senha de conexão deve corresponder às credenciais do PostgreSQL.

Inicie o banco de dados:

```bash
docker compose up -d
```

Execute as migrações:

```bash
poetry run alembic upgrade head
```

Inicie a API:

```bash
poetry run task run
```

A documentação interativa estará disponível em:

`http://127.0.0.1:8000/docs`

## Testes e qualidade

Para executar os testes automatizados:

```bash
poetry run task test
```

Para executar o lint:

```bash
poetry run task lint
```

Os testes utilizam PostgreSQL em containers para verificar a integração da API com o banco de dados.

## Sobre o projeto

O MADR é desenvolvido como projeto de estudo e portfólio, com base no desafio final do [FastAPI do Zero](https://fastapidozero.dunossauro.com/).

O desenvolvimento continua em andamento, e este README será atualizado conforme as funcionalidades forem concluídas.

## Autor

Felipe Vieira — [GitHub](https://github.com/FelipeMNV)
