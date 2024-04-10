from fastapi import HTTPException, status

from src.config import settings


def check_admin(
    user_name: str,
) -> bool:
    admin_list = settings.ALLOWED_USERS.split(", ")
    if user_name in admin_list:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="no access",
    )
