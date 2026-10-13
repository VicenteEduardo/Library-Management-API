# Library Management API

## Objetivo

Este projeto é uma API simples para gerir uma biblioteca: registar livros,
registar membros, emprestar e devolver livros e ver quem está em atraso.

Foi feito para praticar uma organização limpa do código (DDD + SOLID):
o domínio não conhece a base de dados, os casos de uso orquestram as regras
e a API HTTP é só a porta de entrada.

## Como abrir o projeto

1. Abre a pasta `Library Management API` no teu editor (ex. VS Code).
2. Estrutura:
   - `app/domain/` — regras e entidades (livro, membro, empréstimo)
   - `app/application/` — casos de uso (criar livro, emprestar, devolver…)
   - `app/infrastructure/` — base de dados SQLite e repositórios
   - `app/interfaces/api/` — rotas HTTP e schemas
   - `tests/` — testes

## Como correr

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Swagger (para testar no browser): http://127.0.0.1:8000/docs
- Health check: `GET /` devolve `{"status": "ok"}`
- Para parar: `Ctrl + C`

## Como testar

```bash
source .venv/bin/activate
pytest -q
```

Para ver cada teste com detalhe:

```bash
pytest tests/test_api.py -v
pytest tests/test_domain.py -v
pytest tests/test_use_cases.py -v
```

## O que a API faz

- Livros: `POST /books`, `GET /books`, `GET /books/{id}`, `PUT /books/{id}`, `DELETE /books/{id}`
- Membros: `POST /members`, `GET /members`, `GET /members/{id}`, `PUT /members/{id}`, `DELETE /members/{id}`
- Empréstimos: `POST /loans/borrow`, `POST /loans/{id}/return`, `GET /loans`, `GET /loans/overdue`, `GET /loans/{id}`

## Regras da biblioteca

- Cada ISBN e cada email só pode existir uma vez (devolve 409 se repetir).
- Para emprestar: o livro tem de ter cópias livres, o membro tem de estar
  ativo, no máximo 3 empréstimos ativos por membro e sem repetir o mesmo livro.
- Ao devolver, a cópia volta a ficar disponível.
- Não dá para apagar um membro que ainda tenha livros emprestados (devolve 400).
