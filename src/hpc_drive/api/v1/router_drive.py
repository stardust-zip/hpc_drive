import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

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

    **Body Example (JSON):**
    ```json
    {
        "name": "My New Folder",
        "item_type": "FOLDER",
        "parent_id": null
    }
    ```
    """
    return crud.create_drive_item(db=db, item=item, owner_id=current_user.user_id)


@router.get("/items", response_model=schemas.DriveItemListResponse)
def list_items_in_folder(
    parent_id: Optional[uuid.UUID] = None,  # Pass as query parameter
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
    return crud.get_drive_item(
        db=db,
        item_id=item_id,
        user_id=current_user.user_id,  # Use the modified CRUD function
    )


@router.post(
    "/upload",
    response_model=schemas.DriveItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_file(
    file: UploadFile = File(...),
    parent_id: Optional[uuid.UUID] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Uploads a file. This endpoint accepts multipart/form-data.

    The file is saved to a user-specific directory, and both a
    DriveItem and a FileMetadata record are created.

    **Body (form-data):**
    - `file`: The file to upload (e.g., `my_document.pdf`)
    - `parent_id`: (Optional) The UUID of the parent folder.
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
    (No request body)
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
    (No request body)
    """
    return crud.restore_item(db=db, item_id=item_id, owner_id=current_user.user_id)


@router.get("/trash", response_model=List[schemas.DriveItemResponse])
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

    **Body Example (JSON) - To rename:**
    ```json
    {
        "name": "My Renamed Folder"
    }
    ```

    **Body Example (JSON) - To move:**
    ```json
    {
        "parent_id": "a1b2c3d4-..."
    }
    ```
    """
    return crud.update_drive_item(
        db=db, item_id=item_id, owner_id=current_user.user_id, update_data=update_data
    )


@router.post(
    "/items/{item_id}/share",
    response_model=schemas.SharePermissionResponse,
    tags=["Sharing"],  # Add a new tag
)
def share_an_item(
    item_id: uuid.UUID,
    share_data: schemas.ShareCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    """
    Shares an item you own with another user (by username).
    Currently defaults to VIEWER permission.

    **Body Example (JSON):**
    ```json
    {
        "username": "gv_GV001"
    }
    ```
    """
    return crud.share_item(
        db=db, item_id=item_id, owner_id=current_user.user_id, share_data=share_data
    )


@router.get(
    "/shared-with-me", response_model=List[schemas.DriveItemResponse], tags=["Sharing"]
)
def get_items_shared_with_me(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_session)
):
    """
    Lists all items that have been shared with the current user.
    """
    return crud.get_shared_with_me_items(db=db, user_id=current_user.user_id)
