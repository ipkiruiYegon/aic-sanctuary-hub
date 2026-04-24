import jwt
import uuid
from fastapi import Request
from passlib import context
from datetime import datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings


pwd_context = context.CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRY = 3600


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# utils/text_cleaner.py

def clean_and_title(text: str, acronyms=None) -> str:
    """
    Trim spaces, normalize spacing, and convert to title case.
    Preserves acronyms if provided.
    """
    if acronyms is None:
        acronyms = ["AIC", "RCC", "DCC", "LCC", "CED", "CMD", "CYA", "AICMD"]

    # Step 1: Trim leading/trailing spaces
    trimmed = text.strip()

    # Step 2: Normalize multiple spaces
    normalized = ' '.join(trimmed.split())

    # Step 3: Title case
    words = normalized.title().split()

    # Step 4: Restore acronyms
    words = [w.upper() if w.upper() in acronyms else w for w in words]

    return ' '.join(words)


def resolve_role_from_audit(audit_trail: dict) -> str | None:
    """
    Decide the effective role based on audit trail changes.
    Priority: RCC > DCC > None
    """
    has_rcc = "rcc_role" in audit_trail and audit_trail["rcc_role"]["new"]
    has_dcc = "dcc_role" in audit_trail and audit_trail["dcc_role"]["new"]
    has_lcc = "lcc_role" in audit_trail and audit_trail["lcc_role"]["new"]

    if has_rcc and has_dcc:
        return audit_trail["rcc_role"]["new"]  # highest role
    elif has_rcc:
        return audit_trail["rcc_role"]["new"]
    elif has_dcc:
        return audit_trail["dcc_role"]["new"]
    elif has_lcc:
        return audit_trail["lcc_role"]["new"]
    return None


def generate_expiry(expiry: int | None, default: int = ACCESS_TOKEN_EXPIRY) -> int:
    seconds = expiry if (expiry is not None and isinstance(
        expiry, int) and expiry > 0) else default
    return int((datetime.now() + timedelta(seconds=seconds)).timestamp())


def create_access_token(
    user_data: dict, expiry: int = None, refresh: bool = False
):
    payload = {}

    payload["user"] = user_data
    payload["exp"] = generate_expiry(expiry=expiry)

    payload["jti"] = str(uuid.uuid4())

    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, key=settings.JWT_SECRET, algorithms=[
                settings.JWT_ALGORITHM]
        )

        return token_data

    except jwt.PyJWTError as e:
        # logging.exception(e)
        return None


def get_request_token(request: Request):
    # Get token from cookie or header
    token = request.cookies.get("access_token")

    if not token and "Authorization" in request.headers:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    return token
