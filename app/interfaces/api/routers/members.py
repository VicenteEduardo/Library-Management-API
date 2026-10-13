from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases import (
    CreateMember,
    DeleteMember,
    GetMember,
    ListMembers,
    UpdateMember,
)
from app.domain.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.infrastructure.repositories import (
    SQLAlchemyLoanRepository,
    SQLAlchemyMemberRepository,
)
from app.interfaces.api.dependencies import get_loan_repo, get_member_repo
from app.interfaces.api.schemas import MemberCreate, MemberResponse, MemberUpdate

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=MemberResponse,
             status_code=status.HTTP_201_CREATED, summary="Cadastrar membro")
def create_member(payload: MemberCreate,
                  repo: SQLAlchemyMemberRepository = Depends(get_member_repo)):
    try:
        m = CreateMember(repo).execute(**payload.model_dump())
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return MemberResponse(id=m.id, name=m.name, email=m.email,
                          is_active=m.is_active)


@router.get("", response_model=list[MemberResponse], summary="Listar membros")
def list_members(skip: int = 0, limit: int = 100,
                 repo: SQLAlchemyMemberRepository = Depends(get_member_repo)):
    return [MemberResponse(id=m.id, name=m.name, email=m.email,
                           is_active=m.is_active)
            for m in ListMembers(repo).execute(skip, limit)]


@router.get("/{member_id}", response_model=MemberResponse,
            summary="Obter membro")
def get_member(member_id: int,
               repo: SQLAlchemyMemberRepository = Depends(get_member_repo)):
    try:
        m = GetMember(repo).execute(member_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return MemberResponse(id=m.id, name=m.name, email=m.email,
                          is_active=m.is_active)


@router.put("/{member_id}", response_model=MemberResponse,
            summary="Atualizar membro")
def update_member(member_id: int, payload: MemberUpdate,
                  repo: SQLAlchemyMemberRepository = Depends(get_member_repo)):
    try:
        data = {k: v for k, v in payload.model_dump().items() if v is not None}
        m = UpdateMember(repo).execute(member_id, **data)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return MemberResponse(id=m.id, name=m.name, email=m.email,
                          is_active=m.is_active)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Remover membro")
def delete_member(member_id: int,
                  repo: SQLAlchemyMemberRepository = Depends(get_member_repo),
                  loans: SQLAlchemyLoanRepository = Depends(get_loan_repo)):
    try:
        DeleteMember(repo, loans).execute(member_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except BusinessRuleError as e:
        raise HTTPException(status_code=400, detail=str(e))
