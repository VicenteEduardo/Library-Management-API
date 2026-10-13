# Library Management API

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-teal)
![Tests](https://img.shields.io/badge/tests-15%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Uma API simples para gerir uma biblioteca: livros, membros, empréstimos,
devoluções e atrasos. Com documentação interativa (Swagger) e testes.

## Objetivo

Servir de projeto completo e legível para gerir uma biblioteca pequena,
organizado de forma limpa: as regras vivem no domínio, os casos de uso
orquestram as ações e a API HTTP é só a porta de entrada.

## Começar em 2 minutos

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py          # cria livros e membros de exemplo (opcional)
uvicorn app.main:app --reload
```

Abre http://127.0.0.1:8000/docs para explorar e testar tudo no browser.
Para parar: `Ctrl + C`.

Atalhos (`make run`, `make seed`, `make test`) se tiveres `make`.

## Como abrir o projeto

Abre a pasta `Library Management API` no teu editor. O essencial:

```
app/domain/         o que é um livro, membro e empréstimo + regras
app/application/    casos de uso: criar, emprestar, devolver…
app/infrastructure/ base de dados SQLite e repositórios
app/interfaces/api/ rotas HTTP, schemas e Swagger
tests/              testes (domínio, casos de uso e API)
seed.py             dados de exemplo
```

## Exemplos

```bash
# criar um livro
curl -X POST localhost:8000/books \
  -H 'Content-Type: application/json' \
  -d '{"title":"Dom Casmurro","author":"Machado de Assis","isbn":"978-8535914844","total_copies":3}'

# pesquisar
curl 'localhost:8000/books?q=machado'

# criar um membro
curl -X POST localhost:8000/members \
  -H 'Content-Type: application/json' \
  -d '{"name":"Ana","email":"ana@mail.com"}'

# emprestar e devolver
curl -X POST localhost:8000/loans/borrow \
  -H 'Content-Type: application/json' \
  -d '{"book_id":1,"member_id":1}'
curl -X POST localhost:8000/loans/1/return

# em atraso
curl localhost:8000/loans/overdue
```

## Endpoints

| Área       | Método | Rota                  | O que faz              |
| ---------- | ------ | --------------------- | ---------------------- |
| Livros     | POST   | `/books`              | Cadastrar livro        |
| Livros     | GET    | `/books`              | Listar / pesquisar (`q`, `author`) |
| Livros     | GET    | `/books/{id}`         | Obter um livro         |
| Livros     | PUT    | `/books/{id}`         | Atualizar livro        |
| Livros     | DELETE | `/books/{id}`         | Remover livro          |
| Membros    | POST   | `/members`            | Cadastrar membro       |
| Membros    | GET    | `/members`            | Listar membros         |
| Membros    | GET    | `/members/{id}`       | Obter um membro        |
| Membros    | PUT    | `/members/{id}`       | Atualizar membro       |
| Membros    | DELETE | `/members/{id}`       | Remover membro         |
| Empréstimos| POST   | `/loans/borrow`       | Emprestar livro        |
| Empréstimos| POST   | `/loans/{id}/return`  | Devolver livro         |
| Empréstimos| GET    | `/loans`              | Listar empréstimos     |
| Empréstimos| GET    | `/loans/overdue`      | Ver atrasos            |
| Empréstimos| GET    | `/loans/{id}`         | Obter um empréstimo    |

## Regras da biblioteca

- ISBN e email são únicos (409 se repetir).
- Empréstimo: precisa de cópias livres, membro ativo, máx. 3 ativos por membro,
  sem repetir o mesmo livro (400 se falhar).
- Devolver repõe a cópia sem passar do total.
- Membro com empréstimos ativos não pode ser apagado (400).

## Testes

```bash
source .venv/bin/activate
pytest -q
```

## Configuração

Por omissão usa `sqlite:///./library.db`. Para mudar:

```bash
cp .env.example .env   # e edita DATABASE_URL
```

## Licença

MIT — ver `LICENSE`.
