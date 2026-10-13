"""Os formatos do que entra e sai pela API (pedidos e respostas)."""
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


# --- Books ---
class BookCreate(BaseModel):
    title: str = Field(..., examples=["Dom Casmurro"])
    author: str = Field(..., examples=["Machado de Assis"])
    isbn: str = Field(..., examples=["978-8535914844"])
    total_copies: int = Field(default=1, ge=1)
    published_year: Optional[int] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    total_copies: Optional[int] = Field(default=None, ge=1)
    available_copies: Optional[int] = Field(default=None, ge=0)
    published_year: Optional[int] = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    total_copies: int
    available_copies: int
    published_year: Optional[int] = None
    is_available: bool = True

    model_config = {"from_attributes": True}


# --- Members ---
class MemberCreate(BaseModel):
    name: str
    email: str


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class MemberResponse(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool

    model_config = {"from_attributes": True}


# --- Loans ---
class BorrowRequest(BaseModel):
    book_id: int
    member_id: int
    days: int = Field(default=14, ge=1, le=60)


class LoanResponse(BaseModel):
    id: int
    book_id: int
    member_id: int
    loan_date: date
    due_date: date
    return_date: Optional[date] = None
    is_overdue: bool = False

    model_config = {"from_attributes": True}
