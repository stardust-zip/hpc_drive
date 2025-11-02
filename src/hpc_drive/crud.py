import uuid
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, func
from fastapi import HTTPException, status
from datetime import datetime

from . import models, schemas
from .models import ItemType, ShareLevel, Permission


def create_drive_item(
    db: Session, item: schemas.DriveItemCreate, owner_id: int
) -> models.DriveItem:
    """
    Creates a new DriveItem (FILE or FOLDER) in the database.
    """

    # Create the new item instance
    db_item = models.DriveItem(
        name=item.name,
        item_type=item.item_type,
        parent_id=item.parent_id,
        owner_id=owner_id,
    )

    db.add(db_item)

    try:
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError:
        db.rollback()
        # This catches our unique constraint (uq_owner_parent_name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An item with the name '{item.name}' already exists in this folder.",
        )


def get_user_items_in_folder(
    db: Session, owner_id: int, parent_id: uuid.UUID | None
) -> list[models.DriveItem]:
    """
    Gets all non-trashed items for a specific user within a specific folder.
    If parent_id is None, it fetches items from the user's root.
    """
    return (
        db.query(models.DriveItem)
        .options(joinedload(models.DriveItem.file_metadata))
        .filter(
            models.DriveItem.owner_id == owner_id,
            models.DriveItem.parent_id == parent_id,
            models.DriveItem.is_trashed == False,
        )
        .order_by(models.DriveItem.item_type, models.DriveItem.name)
        .all()
    )


def get_drive_item(
    db: Session,
    item_id: uuid.UUID,
    owner_id: int,  # We need this to check permission
) -> models.DriveItem:
    """
    Gets a single drive item, checking for ownership.
    """
    db_item = (
        db.query(models.DriveItem)
        .options(joinedload(models.DriveItem.file_metadata))
        .filter(models.DriveItem.item_id == item_id)
        .first()
    )

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # TODO: Add logic for shared items
    if db_item.owner_id != owner_id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to access this item"
        )

    return db_item


def create_file_with_metadata(
    db: Session,
    owner_id: int,
    filename: str,
    parent_id: uuid.UUID | None,
    mime_type: str,
    size: int,
    storage_path: str,
) -> models.DriveItem:
    """
    Atomically creates a DriveItem (as FILE) and its FileMetadata.
    """

    # 1. Create the DriveItem
    db_item = models.DriveItem(
        name=filename,
        item_type=ItemType.FILE,  # Use the enum
        parent_id=parent_id,
        owner_id=owner_id,
    )
    db.add(db_item)

    try:
        # We flush to get the db_item.item_id assigned by the DB
        db.flush()

        # 2. Create the FileMetadata using the new item_id
        db_metadata = models.FileMetadata(
            item_id=db_item.item_id,
            mime_type=mime_type,
            size=size,
            storage_path=storage_path,
        )
        db.add(db_metadata)

        # 3. Commit both records at once
        db.commit()

        db.refresh(db_item)
        # We need to refresh the metadata relation as well
        db.refresh(db_item, ["file_metadata"])
        return db_item

    except IntegrityError:
        db.rollback()
        # This catches our unique constraint (uq_owner_parent_name)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A file with the name '{filename}' already exists in this folder.",
        )
    except Exception as e:
        db.rollback()
        # Handle other potential errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the file: {e}",
        )


def get_item_for_owner(
    db: Session, item_id: uuid.UUID, owner_id: int
) -> models.DriveItem:
    """
    A helper to get an item IF the user is the owner.
    This is the base for most update/delete operations.
    """
    db_item = (
        db.query(models.DriveItem)
        .filter(
            models.DriveItem.item_id == item_id, models.DriveItem.owner_id == owner_id
        )
        .first()
    )

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or you do not have permission",
        )
    return db_item


def trash_item(db: Session, item_id: uuid.UUID, owner_id: int) -> models.DriveItem:
    """
    Moves an item (and its children, if a folder) to the trash.
    """
    db_item = get_item_for_owner(db, item_id, owner_id)

    if db_item.is_trashed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Item is already in trash"
        )

    # TODO: We need to handle recursive trashing for folders.
    # For now, we'll just trash the single item.

    db_item.is_trashed = True
    db_item.trashed_at = datetime.utcnow()

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def restore_item(db: Session, item_id: uuid.UUID, owner_id: int) -> models.DriveItem:
    """
    Restores an item from the trash.
    """
    db_item = get_item_for_owner(db, item_id, owner_id)

    if not db_item.is_trashed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Item is not in trash"
        )

    # TODO: We need to handle recursive restoring for folders.

    db_item.is_trashed = False
    db_item.trashed_at = None

    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_user_trash(db: Session, owner_id: int) -> list[models.DriveItem]:
    """
    Gets all items for a user that are currently in the trash.
    """
    return (
        db.query(models.DriveItem)
        .options(joinedload(models.DriveItem.file_metadata))
        .filter(
            models.DriveItem.owner_id == owner_id, models.DriveItem.is_trashed == True
        )
        .order_by(models.DriveItem.trashed_at.desc())
        .all()
    )


def check_for_name_conflict(
    db: Session,
    owner_id: int,
    parent_id: uuid.UUID | None,
    name: str,
    exclude_item_id: uuid.UUID | None = None,
):
    """
    Helper function to check for unique constraint violations before committing.
    """
    query = db.query(models.DriveItem).filter(
        models.DriveItem.owner_id == owner_id,
        models.DriveItem.parent_id == parent_id,
        models.DriveItem.name == name,
    )

    if exclude_item_id:
        # Exclude the item itself when checking (e.g., just changing parent_id)
        query = query.filter(models.DriveItem.item_id != exclude_item_id)

    if query.first():
        # A conflict exists
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An item with the name '{name}' already exists in this folder.",
        )


def update_drive_item(
    db: Session, item_id: uuid.UUID, owner_id: int, update_data: schemas.DriveItemUpdate
) -> models.DriveItem:
    """
    Updates a DriveItem's name or parent folder.
    """
    db_item = get_item_for_owner(db, item_id, owner_id)

    if update_data.name is None and update_data.parent_id is None:
        # Nothing to update
        return db_item

    # Determine the final name and parent_id
    new_name = update_data.name if update_data.name is not None else db_item.name
    new_parent_id = (
        update_data.parent_id
        if update_data.parent_id is not None
        else db_item.parent_id
    )

    if new_name == db_item.name and new_parent_id == db_item.parent_id:
        # No actual change
        return db_item

    # Check for name conflicts BEFORE making the change
    check_for_name_conflict(
        db=db,
        owner_id=owner_id,
        parent_id=new_parent_id,
        name=new_name,
        exclude_item_id=item_id,  # Exclude self if parent_id is unchanged
    )

    # Apply the changes
    if update_data.name is not None:
        db_item.name = update_data.name

    if update_data.parent_id is not None:
        # TODO: Check if moving a folder into its own descendant
        db_item.parent_id = update_data.parent_id

    db_item.updated_at = datetime.utcnow()

    try:
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    except IntegrityError:
        # This is a final fallback, though check_for_name_conflict should catch it
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An item with the name '{new_name}' already exists in this folder.",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )


def get_user_by_username(db: Session, username: str) -> models.User | None:
    """Finds a user by their username."""
    return db.query(models.User).filter(models.User.username == username).first()


def share_item(
    db: Session, item_id: uuid.UUID, owner_id: int, share_data: schemas.ShareCreate
) -> models.SharePermission:
    """
    Shares an item with another user.
    """
    # 1. Verify the current user owns the item
    db_item = get_item_for_owner(db, item_id, owner_id)

    # 2. Find the user to share with
    user_to_share_with = get_user_by_username(db, share_data.username)

    if not user_to_share_with:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{share_data.username}' not found",
        )

    if user_to_share_with.user_id == owner_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot share an item with yourself",
        )

    # 3. Check if it's already shared with this user
    existing_share = (
        db.query(models.SharePermission)
        .filter(
            models.SharePermission.item_id == item_id,
            models.SharePermission.shared_with_user_id == user_to_share_with.user_id,
        )
        .first()
    )

    if existing_share:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Item is already shared with {share_data.username}",
        )

    # 4. Create the SharePermission record (default to VIEWER)
    db_share = models.SharePermission(
        item_id=item_id,
        shared_with_user_id=user_to_share_with.user_id,
        permission_level=ShareLevel.VIEWER,  # Default as requested
    )

    # 5. Update the item's main permission status to SHARED
    db_item.permission = Permission.SHARED

    try:
        db.add(db_share)
        db.add(db_item)  # Add the updated item as well
        db.commit()
        db.refresh(db_share)
        return db_share
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to share item: {e}",
        )


def get_shared_with_me_items(db: Session, user_id: int) -> list[models.DriveItem]:
    """
    Gets all items that have been shared with the current user.
    """
    # Find all DriveItems linked to SharePermission records for this user
    return (
        db.query(models.DriveItem)
        .join(models.SharePermission)
        .filter(models.SharePermission.shared_with_user_id == user_id)
        .options(joinedload(models.DriveItem.file_metadata))
        .filter(models.DriveItem.is_trashed == False)
        .all()
    )


# --- MODIFIED: get_drive_item ---


def get_drive_item(
    db: Session,
    item_id: uuid.UUID,
    user_id: int,  # Renamed from owner_id to reflect new logic
) -> models.DriveItem:
    """
    Gets a single drive item.
    A user can access if:
    1. They are the owner.
    2. The item has a SharePermission for them.
    """
    db_item = (
        db.query(models.DriveItem)
        .options(joinedload(models.DriveItem.file_metadata))
        .filter(models.DriveItem.item_id == item_id)
        .first()
    )

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_item.is_trashed and db_item.owner_id != user_id:
        # Only the owner can see their own trashed items
        raise HTTPException(status_code=404, detail="Item not found")

    # Check for ownership
    if db_item.owner_id == user_id:
        return db_item

    # Check for share permission
    is_shared_with_user = (
        db.query(models.SharePermission)
        .filter(
            models.SharePermission.item_id == item_id,
            models.SharePermission.shared_with_user_id == user_id,
        )
        .first()
    )

    if is_shared_with_user:
        # As per requirement, shared users can "view"
        return db_item

    # If neither, they don't have permission
    raise HTTPException(
        status_code=403, detail="You do not have permission to access this item"
    )


def search_items(
    db: Session, user_id: int, query: schemas.DriveItemSearchQuery
) -> list[models.DriveItem]:
    """
    Searches for items based on a set of criteria.

    A user can find:
    1. Items they own.
    2. Items shared with them.

    Filters are applied on top of this.
    """

    # Base query: Find all items the user has access to
    # (owned OR shared with them) and are not in the trash.
    base_query = (
        db.query(models.DriveItem)
        .outerjoin(models.SharePermission)
        .filter(
            or_(
                models.DriveItem.owner_id == user_id,
                models.SharePermission.shared_with_user_id == user_id,
            ),
            models.DriveItem.is_trashed == False,
        )
        .options(joinedload(models.DriveItem.file_metadata))
        .distinct()
    )  # Use distinct to avoid duplicates if owned AND shared

    # --- Apply Dynamic Filters ---

    if query.name:
        # Use 'ilike' for case-insensitive partial matching
        base_query = base_query.filter(models.DriveItem.name.ilike(f"%{query.name}%"))

    if query.item_type:
        base_query = base_query.filter(models.DriveItem.item_type == query.item_type)

    if query.mime_type:
        # This filter only works for files, so we join FileMetadata
        base_query = base_query.join(models.FileMetadata).filter(
            models.FileMetadata.mime_type.ilike(f"%{query.mime_type}%")
        )

    return base_query.order_by(models.DriveItem.name).all()
