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


# --- Python Enums (dịch từ Prisma) ---
# These are the plain Python enums
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


# --- Models ---


class User(Base):
    """
    Bản sao cục bộ của người dùng từ Auth Service.
    userId được đồng bộ từ 'sub' của JWT/Auth Service.
    """

    __tablename__: str = "users"

    # KHÔNG tự động tăng. Nó đến từ auth service 'id'/'sub'.
    userId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)

    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole))
    createdAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relations
    ownedItems: Mapped[list["DriveItem"]] = relationship(back_populates="owner")
    sharedWithMe: Mapped[list["SharePermission"]] = relationship(
        back_populates="sharedWithUser"
    )


class DriveItem(Base):
    """
    Represents a file or folder in the drive.
    """

    __tablename__: str = "drive_items"

    itemId: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255))
    itemType: Mapped[ItemType] = mapped_column(SAEnum(ItemType))
    isTrashed: Mapped[bool] = mapped_column(Boolean, default=False)
    trashedAt: Mapped[datetime | None] = mapped_column(DateTime)
    permission: Mapped[Permission] = mapped_column(
        SAEnum(Permission), default=Permission.PRIVATE
    )
    createdAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updatedAt: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    # Foreign Keys
    ownerId: Mapped[int] = mapped_column(ForeignKey("users.userId"))
    parentId: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("drive_items.itemId"))

    # Relations
    owner: Mapped["User"] = relationship(back_populates="ownedItems")

    # Tự tham chiếu cho cấu trúc folder
    parent: Mapped["DriveItem | None"] = relationship(
        back_populates="children", remote_side="DriveItem.itemId"
    )
    children: Mapped[list["DriveItem"]] = relationship(back_populates="parent")

    # One-to-one relationship
    fileMetadata: Mapped["FileMetadata | None"] = relationship(
        back_populates="driveItem"
    )

    # One-to-many relationship
    sharePermissions: Mapped[list["SharePermission"]] = relationship(
        back_populates="item"
    )

    # Unique constraint (ownerId, parentId, name)
    __table_args__: tuple[UniqueConstraint] = (
        UniqueConstraint("ownerId", "parentId", "name", name="uq_owner_parent_name"),
    )


class FileMetadata(Base):
    """
    Stores metadata for items of type FILE.
    """

    __tablename__: str = "file_metadata"

    # This is both the Primary Key and the Foreign Key, enforcing a one-to-one
    itemId: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("drive_items.itemId"), primary_key=True
    )

    mimeType: Mapped[str] = mapped_column(String(255))
    size: Mapped[int] = mapped_column(BigInteger)
    storagePath: Mapped[str] = mapped_column(String(1024), unique=True)
    documentType: Mapped[DocumentType | None] = mapped_column(SAEnum(DocumentType))
    version: Mapped[int] = mapped_column(Integer, default=1)
    createdAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updatedAt: Mapped[datetime | None] = mapped_column(DateTime, onupdate=func.now())

    # Relations (back-populates for one-to-one)
    driveItem: Mapped["DriveItem"] = relationship(back_populates="fileMetadata")


class SharePermission(Base):
    """
    Represents the permission granted to a user for a specific DriveItem.
    """

    __tablename__: str = "share_permissions"

    shareId: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    permissionLevel: Mapped[ShareLevel] = mapped_column(SAEnum(ShareLevel))
    createdAt: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Foreign Keys
    itemId: Mapped[uuid.UUID] = mapped_column(ForeignKey("drive_items.itemId"))
    sharedWithUserId: Mapped[int] = mapped_column(ForeignKey("users.userId"))

    # Relations
    item: Mapped["DriveItem"] = relationship(back_populates="sharePermissions")
    sharedWithUser: Mapped["User"] = relationship(back_populates="sharedWithMe")

    # Unique constraint (itemId, sharedWithUserId)
    __table_args__: tuple[UniqueConstraint] = (
        UniqueConstraint("itemId", "sharedWithUserId", name="uq_item_shared_user"),
    )
