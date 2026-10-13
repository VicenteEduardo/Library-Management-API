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


def test_search_books_by_title_and_author():
    client.post("/books", json={"title": "Sapiens", "author": "Yuval Harari",
                                "isbn": "SEARCH-1"})
    client.post("/books", json={"title": "Outro", "author": "Alguém",
                                "isbn": "SEARCH-2"})
    assert any(b["isbn"] == "SEARCH-1"
               for b in client.get("/books?q=sapiens").json())
    assert any(b["isbn"] == "SEARCH-1"
               for b in client.get("/books?author=harari").json())


def test_member_update_and_delete():
    m = client.post("/members", json={"name": "Carlos",
                                      "email": "carlos@mail.com"}).json()
    r = client.put(f"/members/{m['id']}", json={"name": "Carlos S"})
    assert r.status_code == 200
    assert r.json()["name"] == "Carlos S"
    assert client.delete(f"/members/{m['id']}").status_code == 204


def test_cannot_delete_member_with_active_loan():
    book = client.post("/books", json={"title": "L", "author": "A",
                                       "isbn": "NODEL-1",
                                       "total_copies": 2}).json()
    m = client.post("/members", json={"name": "Diana",
                                      "email": "diana@mail.com"}).json()
    client.post("/loans/borrow", json={"book_id": book["id"],
                                       "member_id": m["id"]})
    assert client.delete(f"/members/{m['id']}").status_code == 400


def test_get_loan_by_id():
    book = client.post("/books", json={"title": "G", "author": "A",
                                       "isbn": "GETL-1",
                                       "total_copies": 2}).json()
    m = client.post("/members", json={"name": "Eva",
                                      "email": "eva@mail.com"}).json()
    loan = client.post("/loans/borrow", json={"book_id": book["id"],
                                              "member_id": m["id"]}).json()
    r = client.get(f"/loans/{loan['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == loan["id"]
    assert client.get("/loans/999999").status_code == 404
