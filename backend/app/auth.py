from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from .database import DbSession, database_error
from .models import User
from .schemas import LoginRequest, TokenResponse, UserSummary
from .security import TOKEN_TTL_SECONDS, issue_token, signing_key, verify_password, verify_token

router = APIRouter(prefix="/auth", tags=["authentication"])
bearer = HTTPBearer(auto_error=False)


def unauthorized() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Invalid or missing credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_signing_key() -> bytes:
    try:
        return signing_key()
    except RuntimeError:
        raise HTTPException(status_code=503, detail="Authentication unavailable.") from None


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession, response: Response):
    key = get_signing_key()
    try:
        user = db.scalar(select(User).where(User.email == payload.email))
    except SQLAlchemyError:
        raise database_error() from None
    if not verify_password(payload.password.get_secret_value(), user.password_hash if user else None):
        raise unauthorized()
    response.headers["Cache-Control"] = "no-store"
    return TokenResponse(access_token=issue_token(user.id, key), expires_in=TOKEN_TTL_SECONDS)


def get_current_user(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    if credentials is None:
        raise unauthorized()
    try:
        user_id, _ = verify_token(credentials.credentials, get_signing_key())
    except ValueError:
        raise unauthorized() from None
    return resolve_user(db, user_id)


def resolve_user(db: DbSession, user_id: int) -> User:
    try:
        user = db.get(User, user_id)
    except SQLAlchemyError:
        raise database_error() from None
    if user is None or user.password_hash is None:
        raise unauthorized()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/me", response_model=UserSummary)
def read_profile(user: CurrentUser):
    return user


def require_admin(user: CurrentUser) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required.")
    return user


AdminUser = Annotated[User, Depends(require_admin)]
