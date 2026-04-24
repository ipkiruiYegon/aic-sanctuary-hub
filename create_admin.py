import asyncio
from getpass import getpass
from typing import TYPE_CHECKING
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.users.models import User
from app.auth.utils import generate_password_hash
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

async_engine = create_async_engine(url=DATABASE_URL, echo=False)


async def create_admin():
    # Ensure to run alembic upgrade to create the tables required.

    async with AsyncSession(async_engine) as session:
        # Check if an administrator already exists
        admin_result = await session.exec(
            select(User).where(User.is_superuser == True)
        )
        existing_admin = admin_result.first()

        if existing_admin:
            print("An administrator already exists:", existing_admin.email)
            return
        # Prompt for fields
        first_name = input("First name: ").strip()
        last_name = input("Last name: ").strip()
        phone = input("Phone Number: ").strip()
        email = input("Email: ").strip()
        # Prompt for password twice
        while True:
            password = getpass("Password: ")
            confirm_password = getpass("Confirm Password: ")

            if password == confirm_password:
                break
            else:
                print("Passwords do not match. Please try again.")

        # Check if user already exists
        result = await session.exec(select(User).where(User.email == email))
        existing = result.first()
        if existing:
            print(f"❌ User '{email}' already exists.")
            return

        # Create admin user
        admin = User(
            title="Mr",
            phone_no=phone,
            first_name=first_name.title(),
            last_name=last_name.title(),
            email=email,
            password_hash=generate_password_hash(password),
            is_superuser=True,
            is_active=True,
            is_staff=True,
            role="System Administrator"
        )
        session.add(admin)
        await session.commit()
        print(f"✅ Admin user '{email}' created successfully.")

if __name__ == "__main__":
    asyncio.run(create_admin())
