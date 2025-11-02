import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuthAccount(BaseModel):
    """
    Matches the 'account' object in the /me response
    """

    username: str
    is_admin: bool


class StudentInfo(BaseModel):
    """
    Matches the 'student_info' object
    """

    student_code: str


class LecturerInfo(BaseModel):
    """
    Matches the 'lecturer_info' object
    """

    lecturer_code: str
    # We only need the fields we plan to use


class UserDataFromAuth(BaseModel):
    """
    Matches the 'data' object in the /me response
    """

    id: int  # This will be our primary key (userId)
    full_name: str
    email: str
    user_type: str  # "student" or "lecturer"
    account: AuthAccount
    student_info: StudentInfo | None = None
    lecturer_info: LecturerInfo | None = None


class AuthMeResponse(BaseModel):
    """
    Matches the top-level structure of the /me response
    """

    message: str
    data: UserDataFromAuth


class FileMetadataResponse(BaseModel):
    """Schema for file-specific metadata"""

    model_config = ConfigDict(from_attributes=True)

    mime_type: str
    size: int
    storage_path: str
    version: int


class DriveItemBase(BaseModel):
    """Base schema for an item (file or folder)"""

    name: str
    item_type: str  # Should be "FILE" or "FOLDER"
    parent_id: uuid.UUID | None = None


class DriveItemCreate(DriveItemBase):
    """Schema used when creating a new item"""

    pass  # Same as base for now


class DriveItemResponse(DriveItemBase):
    """Schema used when returning an item to the user"""

    model_config = ConfigDict(from_attributes=True)

    item_id: uuid.UUID
    owner_id: int
    created_at: datetime
    updated_at: datetime | None = None
    is_trashed: bool

    # Nested metadata, will be None if it's a folder
    file_metadata: FileMetadataResponse | None = None


class DriveItemListResponse(BaseModel):
    """Schema for returning a list of items"""

    parent_id: uuid.UUID | None
    items: list[DriveItemResponse]
