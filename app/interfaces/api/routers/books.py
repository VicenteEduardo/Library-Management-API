from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases import (
    CreateBook,
    DeleteBook,
    GetBook,
    ListBooks,
    UpdateBook,
)
from app.domain.exceptions import ConflictError, NotFoundError
from app.infrastructure.repositories import SQLAlchemyBookRepository
from app.interfaces.api.dependencies import get_book_repo
from app.interfaces.api.schemas import BookCreate, BookResponse, BookUpdate

router = APIRouter(prefix="/books", tags=["books"])


def _to_response(book) -> BookResponse:
    return BookResponse(
        id=book.id, title=book.title, author=book.author, isbn=book.isbn,
        total_copies=book.total_copies,
        available_copies=book.available_copies or 0,
        published_year=book.published_year,
        is_available=book.is_available,
    )


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED,
             summary="Cadastrar livro")
def create_book(payload: BookCreate,
                repo: SQLAlchemyBookRepository = Depends(get_book_repo)):
    try:
        book = CreateBook(repo).execute(**payload.model_dump())
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return _to_response(book)


@router.get("", response_model=list[BookResponse], summary="Listar livros")
def list_books(skip: int = 0, limit: int = 100,
               repo: SQLAlchemyBookRepository = Depends(get_book_repo)):
    return [_to_response(b) for b in ListBooks(repo).execute(skip, limit)]


@router.get("/{book_id}", response_model=BookResponse, summary="Obter livro")
def get_book(book_id: int,
             repo: SQLAlchemyBookRepository = Depends(get_book_repo)):
    try:
        return _to_response(GetBook(repo).execute(book_id))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{book_id}", response_model=BookResponse, summary="Atualizar livro")
def update_book(book_id: int, payload: BookUpdate,
                repo: SQLAlchemyBookRepository = Depends(get_book_repo)):
    try:
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        return _to_response(UpdateBook(repo).execute(book_id, **data))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Remover livro")
def delete_book(book_id: int,
                repo: SQLAlchemyBookRepository = Depends(get_book_repo)):
    try:
        DeleteBook(repo).execute(book_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
