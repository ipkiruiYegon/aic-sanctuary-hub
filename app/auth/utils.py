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
