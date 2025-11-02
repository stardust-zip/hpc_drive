from fastapi import APIRouter, Depends
from sqlmodel import Session

from ...db import get_session
from ...models import User
from ...security import get_current_user

router = APIRouter(prefix="/drive", tags=["Drive"])


@router.get("/me")
def get_user_me(
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint test: Trả về thông tin user đã được
    xác thực và đồng bộ từ DB cục bộ.
    """
    return current_user
