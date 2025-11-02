from pydantic import BaseModel


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
