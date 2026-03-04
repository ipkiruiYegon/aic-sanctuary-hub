from passlib import context

pwd_context = context.CryptContext(schemes=["bcrypt"], deprecated="auto")


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
        acronyms = ["AIC"]

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

    if has_rcc and has_dcc:
        return audit_trail["rcc_role"]["new"]  # highest role
    elif has_rcc:
        return audit_trail["rcc_role"]["new"]
    elif has_dcc:
        return audit_trail["dcc_role"]["new"]
    return None
