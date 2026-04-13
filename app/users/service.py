import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.db.models import User  # Import your User model here
# Import your Pydantic schemas here
from app.users.schemas import UserCreateSchema
from app.auth.utils import generate_password_hash, clean_and_title, resolve_role_from_audit


class UserService:
    async def user_phone_exists(self, phone_number: str, session: AsyncSession):
        # Logic to retrieve a user by ID from the database
        sql_query = select(User).where(User.phone_no == phone_number)
        result = await session.exec(sql_query)
        user = result.first()
        return True if user is not None else False

    async def user_exists(self, user_id: str, session: AsyncSession):
        # Logic to retrieve a user by ID from the database
        sql_query = select(User).where(User.id == user_id)
        result = await session.exec(sql_query)
        user = result.first()
        return True if user is not None else False

    async def get_all_users(self, session: AsyncSession):
        # Logic to retrieve all users from the database
        sql_query = select(User)
        result = await session.exec(sql_query)
        users = result.all()
        return users

    async def get_user_by_phone(self, phone_number: str, session: AsyncSession):
        # Logic to retrieve a user by ID from the database
        sql_query = select(User).where(User.phone_no == phone_number)
        result = await session.exec(sql_query)
        user = result.first()
        return user

    async def create_user(self, user_data: UserCreateSchema, session: AsyncSession):
        # Logic to create a new user in the database
        new_user = User(**user_data.model_dump())
        new_user.title = clean_and_title(user_data.title)
        new_user.first_name = clean_and_title(user_data.first_name)
        new_user.last_name = clean_and_title(user_data.last_name)
        new_user.role = clean_and_title(user_data.role, acronyms=[
                                        "CED", "LCC", "DCC", "RCC", "AIC"])
        new_user.lcc_role = new_user.role

        if new_user.title in ["Pastor", "Reverend", "Bishop"]:
            new_user.is_staff = True

        new_user.password_hash = generate_password_hash(
            "Test@1234")  # Set a default password or generate one as needed
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    async def get_user_by_uid(self, user_id: uuid.UUID, session: AsyncSession):
        # Logic to retrieve a user by ID from the database

        sql = select(User).where(User.id == user_id)
        result = await session.exec(sql)
        user = result.first()
        return user

    async def update_user(self, user_data: dict, session: AsyncSession):
        # Logic to update an existing user in the database
        user = await self.get_user_by_uid(str(user_data["user_id"]), session)
        if not user:
            return False

        audit_trail = {}
        for field, new_value in user_data.items():
            if not hasattr(user, field):
                continue  # skip invalid fields

            old_value = getattr(user, field)
            if new_value != old_value:
                setattr(user, field, new_value)
                audit_trail[field] = {"old": old_value, "new": new_value}

        if audit_trail:
            effective_role = resolve_role_from_audit(audit_trail)
            if effective_role:
                user.role = effective_role   # set effective role field
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return True
        else:
            return False

    async def update_user_status(self, user_id: str, reason: str, session: AsyncSession):
        # Logic to update a user's status in the database
        user = await self.get_user_by_uid(user_id, session)
        if not user:
            return None
        user.is_active = not user.is_active  # Toggle the is_active status
        # Optionally, you can log the reason for status change in an audit trail
        await session.commit()
        await session.refresh(user)
        return user

    async def remove_user_tokens(self, user_id: str, session: AsyncSession):
        # Logic to update a user's status in the database
        user = await self.get_user_by_uid(user_id, session)
        if not user:
            return None
        user.token = None
        user.reset_token = None
        await session.commit()
        await session.refresh(user)
        return user

    async def token_in_user_db(self, user_id: str, token: str, session: AsyncSession) -> bool:
        user = await self.get_user_by_uid(user_id, session)
        if not user:
            return False  # Token is invalid if user doesn't exist
        if not user.token:
            return False  # Token is invalid if user has no token
        if user.token != token:
            return False  # Token is invalid if it doesn't match the user's token
        return True  # Token is valid
