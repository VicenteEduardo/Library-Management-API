"""Enche a base de dados com exemplos para explorar a API à vontade.

Correr:  python seed.py
"""
from app.application.use_cases import BorrowBook, CreateBook, CreateMember
from app.infrastructure.database import Base, SessionLocal, engine
from app.infrastructure import models  # noqa: F401  (regista tabelas)
from app.infrastructure.repositories import (
    SQLAlchemyBookRepository,
    SQLAlchemyLoanRepository,
    SQLAlchemyMemberRepository,
)

BOOKS = [
    ("Dom Casmurro", "Machado de Assis", "978-8535914844", 3, 1899),
    ("Memórias Póstumas de Brás Cubas", "Machado de Assis", "978-8573260824", 2, 1881),
    ("O Pequeno Príncipe", "Antoine de Saint-Exupéry", "978-9722320791", 5, 1943),
    ("Sapiens", "Yuval Noah Harari", "978-9722084067", 2, 2011),
]

MEMBERS = [
    ("Ana Sousa", "ana@mail.com"),
    ("Bruno Costa", "bruno@mail.com"),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        books = SQLAlchemyBookRepository(db)
        members = SQLAlchemyMemberRepository(db)
        loans = SQLAlchemyLoanRepository(db)

        if books.list(limit=1) or members.list(limit=1):
            print("A base de dados já tem dados — nada a fazer.")
            return

        book_ids = [CreateBook(books).execute(t, a, i, c, y).id
                    for t, a, i, c, y in BOOKS]
        member_ids = [CreateMember(members).execute(n, e).id
                      for n, e in MEMBERS]
        BorrowBook(books, members, loans).execute(book_ids[0], member_ids[0])
        print(f"Criados {len(book_ids)} livros, {len(member_ids)} membros e 1 empréstimo.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
