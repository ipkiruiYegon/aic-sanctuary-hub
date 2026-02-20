import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.db.models import User  # Import your User model here
# Import your Pydantic schemas here
from app.users.schemas import UserCreateModel, UserUpdateModel
# Import your password hashing utilities here
from app.auth.utils import generate_password_hash


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
        user_data_dict = user_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.first_name = user_data_dict['first_name'].title()
        new_user.last_name = user_data_dict['last_name'].title()
        new_user.role = user_data_dict['role'].title()
        print(user_data_dict['password'])
        new_user.password_hash = generate_password_hash(
            user_data_dict['password'])
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
