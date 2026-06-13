from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.crm.models import CrmUser
from app.modules.crm.schemas import CrmUserCreate, CrmUserRead, CrmUserStatusUpdate, CrmUserUpdate

router = APIRouter(
    prefix="/crm",
    tags=["crm"],
    dependencies=[Depends(get_current_admin_user)],
)


def crm_user_to_read(user: CrmUser) -> CrmUserRead:
    return CrmUserRead(
        id=user.id,
        username=user.username,
        name=user.name,
        nickname=user.nickname,
        phone=user.phone,
        email=user.email,
        mt5_login=user.mt5_login,
        parent_mt5_login=user.parent_mt5_login,
        parent_id=user.parent_id,
        parent_name=user.parent.name if user.parent else None,
        parent_code=user.parent_code,
        role_type=user.role_type,
        certification_status=user.certification_status,
        status=user.status,
        remark=user.remark,
        created_at=user.created_at,
    )


def get_crm_user_or_404(db: Session, user_id: int) -> CrmUser:
    user = db.scalar(
        select(CrmUser)
        .where(CrmUser.id == user_id)
        .options(selectinload(CrmUser.parent))
    )
    if user is None:
        raise HTTPException(status_code=404, detail="CRM user not found")
    return user


def resolve_parent(
    db: Session,
    parent_id: int | None,
    user_id: int | None = None,
) -> CrmUser | None:
    if parent_id is None:
        return None
    if user_id is not None and parent_id == user_id:
        raise HTTPException(status_code=400, detail="Parent CRM user cannot be self")
    parent = db.get(CrmUser, parent_id)
    if parent is None:
        raise HTTPException(status_code=400, detail="Parent CRM user does not exist")
    return parent


@router.get("/users", response_model=list[CrmUserRead])
def list_crm_users(
    db: Annotated[Session, Depends(get_db)],
    keyword: str | None = None,
    mt5_login: str | None = None,
) -> list[CrmUserRead]:
    query = select(CrmUser).options(selectinload(CrmUser.parent)).order_by(desc(CrmUser.id))
    if keyword:
        keyword_like = f"%{keyword}%"
        query = query.where(
            or_(
                CrmUser.name.like(keyword_like),
                CrmUser.nickname.like(keyword_like),
                CrmUser.phone.like(keyword_like),
                CrmUser.email.like(keyword_like),
            )
        )
    if mt5_login:
        query = query.where(CrmUser.mt5_login == mt5_login)

    users = db.scalars(
        query
    ).all()
    return [crm_user_to_read(user) for user in users]


@router.post("/users", response_model=CrmUserRead, status_code=status.HTTP_201_CREATED)
def create_crm_user(
    payload: CrmUserCreate,
    db: Annotated[Session, Depends(get_db)],
) -> CrmUserRead:
    parent = resolve_parent(db, payload.parent_id)
    user = CrmUser(
        username=payload.username,
        name=payload.name,
        nickname=payload.nickname,
        phone=payload.phone,
        email=payload.email,
        mt5_login=payload.mt5_login,
        parent_mt5_login=payload.parent_mt5_login,
        parent=parent,
        parent_code=payload.parent_code,
        role_type=payload.role_type,
        certification_status=payload.certification_status,
        status=payload.status,
        remark=payload.remark,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return crm_user_to_read(user)


@router.get("/users/{user_id}", response_model=CrmUserRead)
def read_crm_user(user_id: int, db: Annotated[Session, Depends(get_db)]) -> CrmUserRead:
    return crm_user_to_read(get_crm_user_or_404(db, user_id))


@router.put("/users/{user_id}", response_model=CrmUserRead)
def update_crm_user(
    user_id: int,
    payload: CrmUserUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> CrmUserRead:
    user = get_crm_user_or_404(db, user_id)
    user.username = payload.username
    user.name = payload.name
    user.nickname = payload.nickname
    user.phone = payload.phone
    user.email = payload.email
    user.mt5_login = payload.mt5_login
    user.parent_mt5_login = payload.parent_mt5_login
    user.parent = resolve_parent(db, payload.parent_id, user_id)
    user.parent_code = payload.parent_code
    user.role_type = payload.role_type
    user.certification_status = payload.certification_status
    user.status = payload.status
    user.remark = payload.remark
    db.commit()
    db.refresh(user)
    return crm_user_to_read(user)


@router.patch("/users/{user_id}/status", response_model=CrmUserRead)
def update_crm_user_status(
    user_id: int,
    payload: CrmUserStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> CrmUserRead:
    user = get_crm_user_or_404(db, user_id)
    user.status = payload.status
    db.commit()
    db.refresh(user)
    return crm_user_to_read(user)
