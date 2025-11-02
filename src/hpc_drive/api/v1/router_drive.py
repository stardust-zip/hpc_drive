import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

# Updated imports
from ...database import get_session
from ...models import User
from ...security import get_current_user, get_current_user_data_from_auth
from ... import crud, schemas
from ...config import settings

router = APIRouter(prefix="/drive", tags=["Drive"])


@router.get("/me", response_model=schemas.UserDataFromAuth)
def get_user_me(
    current_user_data: schemas.UserDataFromAuth = Depends(
        get_current_user_data_from_auth
    ),
):
    """
    Returns the raw user data payload from the Auth Service.
    This shows what data we get for the synced user.
    """
    return current_user_data


@router.post(
    "/items",
    response_model=schemas.DriveItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_item(
    item: schemas.DriveItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Create a new drive item (FILE or FOLDER) in the root
    or inside a parent folder.
    """
    return crud.create_drive_item(db=db, item=item, owner_id=current_user.user_id)


@router.get("/items", response_model=schemas.DriveItemListResponse)
def list_items_in_folder(
    parent_id: uuid.UUID | None = None,  # Pass as query parameter
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    List all items for the current user within a specific folder.
    If 'parent_id' is not provided, lists items in the root.
    """
    items = crud.get_user_items_in_folder(
        db=db, owner_id=current_user.user_id, parent_id=parent_id
    )
    return {"parent_id": parent_id, "items": items}


@router.get("/items/{item_id}", response_model=schemas.DriveItemResponse)
def get_item_details(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Get the details for a single drive item.
    """
    return crud.get_drive_item(db=db, item_id=item_id, owner_id=current_user.user_id)


@router.post(
    "/upload",
    response_model=schemas.DriveItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_file(
    file: UploadFile = File(...),
    parent_id: uuid.UUID | None = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Uploads a file. This endpoint accepts multipart/form-data.

    The file is saved to a user-specific directory, and both a
    DriveItem and a FileMetadata record are created.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file name provided")

    # 1. Define the storage path
    item_storage_id = uuid.uuid4()
    user_upload_dir = (
        settings.UPLOADS_DIR / str(current_user.user_id) / str(item_storage_id)
    )
    user_upload_dir.mkdir(parents=True, exist_ok=True)
    storage_path = user_upload_dir / file.filename

    # 2. Save the file to disk
    try:
        with storage_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    finally:
        file.file.close()

    # 3. Get file size from the saved file
    file_size = storage_path.stat().st_size

    # ***** THIS IS THE FIX *****
    # Provide a default MIME type if one isn't provided
    mime_type = file.content_type if file.content_type else "application/octet-stream"

    # 4. Call the new CRUD function to create both DB records
    try:
        db_item = crud.create_file_with_metadata(
            db=db,
            owner_id=current_user.user_id,
            filename=file.filename,
            parent_id=parent_id,
            mime_type=mime_type,  # Pass the guaranteed string
            size=file_size,
            storage_path=str(storage_path),
        )
        return db_item
    except HTTPException as e:
        storage_path.unlink()
        user_upload_dir.rmdir()
        raise e


@router.patch("/items/{item_id}/trash", response_model=schemas.DriveItemResponse)
def move_item_to_trash(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Moves an item to the trash (sets is_trashed = True).
    """
    return crud.trash_item(db=db, item_id=item_id, owner_id=current_user.user_id)


@router.patch("/items/{item_id}/restore", response_model=schemas.DriveItemResponse)
def restore_item_from_trash(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Restores an item from the trash (sets is_trashed = False).
    """
    return crud.restore_item(db=db, item_id=item_id, owner_id=current_user.user_id)


@router.get("/trash", response_model=list[schemas.DriveItemResponse])
def get_trashed_items(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_session)
):
    """
    Lists all items belonging to the user that are in the trash.
    """
    return crud.get_user_trash(db=db, owner_id=current_user.user_id)


@router.patch("/items/{item_id}", response_model=schemas.DriveItemResponse)
def update_item_details(
    item_id: uuid.UUID,
    update_data: schemas.DriveItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Updates an item's details, such as its name or parent folder.

    To rename, send: {"name": "new_name"}
    To move, send: {"parent_id": "new_parent_uuid"}
    To do both, send both.
    """
    return crud.update_drive_item(
        db=db, item_id=item_id, owner_id=current_user.user_id, update_data=update_data
    )
