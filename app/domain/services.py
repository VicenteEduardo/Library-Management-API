"""As regras da casa, num só sítio para não se espalharem pelo código."""
from typing import List

from app.domain.entities import Book, Loan
from app.domain.exceptions import BusinessRuleError

MAX_ACTIVE_LOANS_PER_MEMBER = 3


def validate_borrow(book: Book, active_loans: List[Loan]) -> None:
    if not book.is_available:
        raise BusinessRuleError("livro sem cópias disponíveis")
    if len(active_loans) >= MAX_ACTIVE_LOANS_PER_MEMBER:
        raise BusinessRuleError(
            f"membro atingiu o limite de {MAX_ACTIVE_LOANS_PER_MEMBER} empréstimos ativos"
        )
    if any(loan.book_id == book.id for loan in active_loans):
        raise BusinessRuleError("membro já possui este livro emprestado")
