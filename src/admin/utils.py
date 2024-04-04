from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserSchema
from src.config import settings


def check_admin(
    user_name: str,
) -> bool:
    admin_list = settings.ALLOWED_USERS.split(', ')
    if user_name in admin_list:
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="no access",
        )
