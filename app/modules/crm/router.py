from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_admin_user
from app.modules.crm.models import CrmUser
from app.modules.crm.schemas import CrmUserRead

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
        parent_id=user.parent_id,
        parent_name=user.parent.name if user.parent else None,
        parent_code=user.parent_code,
        role_type=user.role_type,
        certification_status=user.certification_status,
        status=user.status,
        remark=user.remark,
        mt5_login=None,
        parent_mt5_login=None,
        created_at=user.created_at,
    )


@router.get("/users", response_model=list[CrmUserRead])
def list_crm_users(db: Annotated[Session, Depends(get_db)]) -> list[CrmUserRead]:
    users = db.scalars(
        select(CrmUser).options(selectinload(CrmUser.parent)).order_by(desc(CrmUser.id))
    ).all()
    return [crm_user_to_read(user) for user in users]
