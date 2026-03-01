import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.db.models import User  # Import your User model here
# Import your Pydantic schemas here
from app.users.schemas import UserCreateModel
from app.auth.utils import generate_password_hash, clean_and_title


class UserService:
    async def user_exists(self, phone_number: str, session: AsyncSession):
        # Logic to retrieve a user by ID from the database
        sql_query = select(User).where(User.phone_no == phone_number)
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
        sql_query = select(User).where(User.phone_number == phone_number)
        result = await session.exec(sql_query)
        user = result.first()
        return user

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):
        # Logic to create a new user in the database
        print(f"Creating user with data: {user_data}")
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

    async def get_user_by_uid(self, user_id: str, session: AsyncSession):
        # Logic to retrieve a user by ID from the database
        try:
            # Convert string to UUID
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            print(f"Invalid UUID string: {user_id}")
            return None

        sql = select(User).where(User.id == user_id)
        result = await session.exec(sql)
        user = result.first()
        print(user)
        return user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        # Logic to update an existing user in the database
        for key, value in user_data.items():
            setattr(user, key, value)
        await session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def delete_user(self, user_id: str, session: AsyncSession):
        # Logic to delete a user from the database
        sql = select(User).where(User.id == user_id)
        result = await session.exec(sql)
        user = result.first()
        if user:
            user.is_active = False  # Soft delete by marking the user as inactive
            await session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        return None
