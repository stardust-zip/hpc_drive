import uuid
from enum import Enum
from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    Boolean,
    BigInteger,
    UniqueConstraint,
    UUID,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func


# --- Base Class ---
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


# --- Python Enums (Unchanged, as they are classes) ---
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class ItemType(str, Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"


class Permission(str, Enum):
    PRIVATE = "PRIVATE"
    SHARED = "SHARED"


class ShareLevel(str, Enum):
    VIEWER = "VIEWER"
    EDITOR = "EDITOR"


class DocumentType(str, Enum):
    PDF = "PDF"
    WORD = "WORD"
    EXCEL = "EXCEL"
    POWERPOINT = "POWERPOINT"
    OTHER = "OTHER"


# --- Models (CONVERTED TO SNAKE_CASE) ---


class User(Base):
    """
    Local cache of a user from the Auth Service.
    All attributes are snake_case.
    """

    __tablename__: str = "users"

    # 'sub' from auth service
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)

    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relations
    owned_items: Mapped[list["DriveItem"]] = relationship(back_populates="owner")
    shared_with_me: Mapped[list["SharePermission"]] = relationship(
        back_populates="shared_with_user"
    )


class DriveItem(Base):
    """
    Represents a file or folder in the drive.
    All attributes are snake_case.
    """

    __tablename__: str = "drive_items"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    item_type: Mapped[ItemType] = mapped_column(SAEnum(ItemType))
    is_trashed: Mapped[bool] = mapped_column(Boolean, default=False)
    trashed_at: Mapped[datetime | None] = mapped_column(DateTime)
    permission: Mapped[Permission] = mapped_column(
        SAEnum(Permission), default=Permission.PRIVATE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    # Foreign Keys
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("drive_items.item_id")
    )

    # Relations
    owner: Mapped["User"] = relationship(back_populates="owned_items")

    parent: Mapped["DriveItem | None"] = relationship(
        back_populates="children", remote_side="DriveItem.item_id"
    )
    children: Mapped[list["DriveItem"]] = relationship(back_populates="parent")

    file_metadata: Mapped["FileMetadata | None"] = relationship(
        back_populates="drive_item"
    )
    share_permissions: Mapped[list["SharePermission"]] = relationship(
        back_populates="item"
    )

    # Unique constraint (owner_id, parent_id, name)
    __table_args__: tuple[UniqueConstraint] = (
        UniqueConstraint("owner_id", "parent_id", "name", name="uq_owner_parent_name"),
    )


class FileMetadata(Base):
    """
    Stores metadata for items of type FILE.
    All attributes are snake_case.
    """

    __tablename__: str = "file_metadata"

    item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("drive_items.item_id"), primary_key=True
    )

    mime_type: Mapped[str] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(BigInteger)
    storage_path: Mapped[str] = mapped_column(String(1024), unique=True)
    document_type: Mapped[DocumentType | None] = mapped_column(SAEnum(DocumentType))
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    # Relations
    drive_item: Mapped["DriveItem"] = relationship(back_populates="file_metadata")


class SharePermission(Base):
    """
    Represents the permission granted to a user for a specific DriveItem.
    All attributes are snake_case.
    """

    __tablename__: str = "share_permissions"

    share_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    permission_level: Mapped[ShareLevel] = mapped_column(SAEnum(ShareLevel))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Foreign Keys
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("drive_items.item_id"))
    shared_with_user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))

    # Relations
    item: Mapped["DriveItem"] = relationship(back_populates="share_permissions")
    shared_with_user: Mapped["User"] = relationship(back_populates="shared_with_me")

    # Unique constraint (item_id, shared_with_user_id)
    __table_args__: tuple[UniqueConstraint] = (
        UniqueConstraint("item_id", "shared_with_user_id", name="uq_item_shared_user"),
    )
