"""Testes da API de ponta a ponta, com uma base de dados em memória só para os testes."""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.infrastructure.database import Base, get_db
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                       poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def test_full_flow_borrow_return():
    book = client.post("/books", json={"title": "Dom Casmurro",
                                       "author": "Machado de Assis",
                                       "isbn": "978-1", "total_copies": 1}).json()
    member = client.post("/members", json={"name": "Ana",
                                            "email": "ana@mail.com"}).json()
    loan = client.post("/loans/borrow",
                       json={"book_id": book["id"],
                             "member_id": member["id"]}).json()
    assert loan["book_id"] == book["id"]
    # sem cópias -> 400
    r = client.post("/loans/borrow",
                    json={"book_id": book["id"], "member_id": member["id"]})
    assert r.status_code == 400
    # devolver
    ret = client.post(f"/loans/{loan['id']}/return").json()
    assert ret["return_date"] is not None
    # overdue vazio
    assert client.get("/loans/overdue").status_code == 200


def test_duplicate_isbn_returns_409():
    client.post("/books", json={"title": "A", "author": "B", "isbn": "DUP-1"})
    r = client.post("/books", json={"title": "A", "author": "B",
                                     "isbn": "DUP-1"})
    assert r.status_code == 409
