import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from ...database import get_session
from ...models import User
from ...security import get_current_admin_user  # Import the new dependency
from ... import crud, schemas

router = APIRouter(prefix="/admin/drive", tags=["Admin - Drive"])

# We use 'Depends(get_current_admin_user)' on every endpoint
# to lock this router down to admins only.


@router.get("/items", response_model=List[schemas.DriveItemResponse])
def get_all_items(
    skip: int = 0,
    limit: int = 100,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session),
):
    """
    [ADMIN] Get a paginated list of all drive items from all users.
    """
    return crud.admin_get_all_items(db=db, skip=skip, limit=limit)


@router.get("/items/{item_id}", response_model=schemas.DriveItemResponse)
def get_item_by_id(
    item_id: uuid.UUID,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session),
):
    """
    [ADMIN] Get the details for any single drive item by its ID.
    """
    return crud.admin_get_item_by_id(db=db, item_id=item_id)


@router.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
def delete_item_permanently(
    item_id: uuid.UUID,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_session),
):
    """
    [ADMIN] Permanently delete any item. This is irreversible.
    """
    return crud.admin_delete_item_permanently(db=db, item_id=item_id)
