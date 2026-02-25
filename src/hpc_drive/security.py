import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from .database import get_session
from .models import User, UserRole

# ---> IMPORT THE SCHEMAS
from .schemas import AuthAccount, UserDataFromAuth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def map_role(user_type: str, is_admin: bool) -> UserRole:
    if is_admin:
        return UserRole.ADMIN
    if user_type == "lecturer":
        return UserRole.TEACHER
    return UserRole.STUDENT


def get_current_user_data_from_token(
    token: str = Depends(oauth2_scheme),
) -> UserDataFromAuth:
    """
    Decodes the JWT and maps it back to the strict Pydantic schema
    so the Frontend and other routers don't break.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_aud": False,
                "verify_iss": False,
                "verify_sub": False,
            },
        )

        if payload.get("sub") is None:
            raise credentials_exception

        # RECONSTRUCT THE NESTED SCHEMA EXPECTED BY PRODUCTION
        return UserDataFromAuth(
            id=int(payload.get("sub")),
            full_name=payload.get("full_name", ""),
            email=payload.get("email", ""),
            user_type=payload.get("user_type", "student"),
            account=AuthAccount(
                username=payload.get("username", ""),
                is_admin=payload.get("is_admin", False),
            ),
        )

    except jwt.ExpiredSignatureError as e:
        print(f"JWT REJECTED -> Token expired: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as e:
        print(f"JWT REJECTED -> {type(e).__name__}: {str(e)}")
        raise credentials_exception


def get_current_user(
    session: Session = Depends(get_session),
    user_data: UserDataFromAuth = Depends(get_current_user_data_from_token),
) -> User:
    """
    Syncs the user from the reconstructed schema to the local database.
    """
    # Now we safely read from the Pydantic object again!
    user_id = user_data.id
    username = user_data.account.username
    email = user_data.email
    user_type = user_data.user_type
    is_admin = user_data.account.is_admin

    new_role = map_role(user_type, is_admin)
    user = session.get(User, user_id)

    if user is None:
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=new_role,
        )
        session.add(user)
    else:
        update_made = False
        if user.username != username:
            user.username = username
            update_made = True
        if user.email != email:
            user.email = email
            update_made = True
        if user.role != new_role:
            user.role = new_role
            update_made = True

        if update_made:
            session.add(user)

    try:
        if session.new or session.dirty:
            session.commit()
            session.refresh(user)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync user profile to local DB",
        )

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    return current_user
