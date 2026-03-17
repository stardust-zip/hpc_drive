import sys

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import crud
from .config import settings
from .database import get_session
from .models import User, UserRole  # Our local SQLModel User
from .schemas import AuthAccount, AuthMeResponse, UserDataFromAuth  # Added AuthAccount

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
    Syncs the user from the reconstructed schema to the local database,
    with built-in protection against Next.js concurrent request race conditions.
    """
    user_id = user_data.id
    username = user_data.account.username
    email = user_data.email
    user_type = user_data.user_type
    is_admin = user_data.account.is_admin

    new_role = map_role(user_type, is_admin)
    user = session.get(User, user_id)

    if user is None:
        # User does not exist locally, create them
        print(f"User not found locally (ID: {user_data.id}). Syncing new user...")

        # ***** CORRECTED TO SNAKE_CASE *****
        # Get default quota from system settings
        sys_settings = crud.get_system_settings(session)
        default_quota_bytes = sys_settings.default_quota_gb * (1024**3)

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            role=new_role,
            storage_quota=default_quota_bytes,
            max_file_size=sys_settings.max_upload_size_mb * (1024**2),
        )
        session.add(user)
        try:
            session.commit()
            session.refresh(user)
        except IntegrityError:
            # RACE CONDITION FIX: Next.js fired two requests at the exact same time.
            # Another thread already created the user a millisecond ago!
            session.rollback()
            user = session.get(User, user_id)
        except Exception as e:
            session.rollback()
            print(f"FATAL DB ERROR (Create): {e}", file=sys.stderr)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to sync user profile to local DB",
            )
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

        # Ensure storage fields are initialized (for existing users after migration)
        if user.storage_quota is None or user.storage_quota == 10737418240:
            # Only update if it's None or the old hardcoded default,
            # and the user doesn't have a custom quota
            if user.custom_storage_quota_gb is None:
                sys_settings = crud.get_system_settings(session)
                user.storage_quota = sys_settings.default_quota_gb * (1024**3)
                update_made = True

        if user.used_storage is None:
            user.used_storage = 0
            update_made = True

        if user.max_file_size is None or user.max_file_size == 2147483648:
            if (
                user.role != UserRole.ADMIN
            ):  # Admins usually have higher limits or handled elsewhere
                sys_settings = crud.get_system_settings(session)
                user.max_file_size = sys_settings.max_upload_size_mb * (1024**2)
                update_made = True

        if update_made:
            session.add(user)

    try:
        session.commit()
        session.refresh(user)
    except Exception as e:
        session.rollback()
        import sqlite3

        from sqlalchemy.exc import IntegrityError

        # Handle parallel requests race condition (another request inserted the user)
        if isinstance(e, IntegrityError) or "UNIQUE constraint failed" in str(e):
            print(
                f"Parallel insert detected for user {user_data.id}, falling back to fetch."
            )
            user = session.get(User, user_data.id)
            if user:
                return user

        print(f"Error committing user sync: {e}")
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
