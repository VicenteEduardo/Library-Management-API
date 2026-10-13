"""O ponto de partida: cria a app, as tabelas e liga as rotas. O Swagger fica em /docs."""
from fastapi import FastAPI

from app.infrastructure.database import Base, engine
from app.infrastructure import models  # noqa: F401  (regista tabelas)
from app.interfaces.api.routers import books, loans, members

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Library Management API",
    description="API para gerir livros, membros e empréstimos. DDD + SOLID.",
    version="1.0.0",
)

app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)


@app.get("/", tags=["health"], summary="Health check")
def health():
    return {"status": "ok"}
