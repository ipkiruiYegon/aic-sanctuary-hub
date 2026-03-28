from fastapi import Depends, HTTPException, status, APIRouter, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta

from app.auth.schemas import LoginModel, PasswordChangeModel
from app.db.database import get_session
from app.users.service import UserService
from app.core import templates
from app.auth.utils import verify_password, create_access_token, get_request_token, decode_token, generate_password_hash


auth_router = APIRouter()
user_services = UserService()

REFRESH_TOKEN_EXPIRY = 2


@auth_router.post("/authenticate")
async def authenticate_users(login_data: LoginModel, session: AsyncSession = Depends(get_session)):
    phone_no = login_data.phone
    password = login_data.password

    user = await user_services.get_user_by_phone(phone_no, session)

    if user is not None:
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User account is inactive")
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            # Check if user is required to change password or activate account
            if not user.linked or user.password_status == "change":
                access_token = create_access_token(
                    user_data={
                        "username": user.first_name,
                        "user_id": str(user.id),
                        "role": user.role,
                    }, expiry=180
                )
                user.token = access_token
                session.add(user)
                await session.commit()
                response = RedirectResponse(
                    url="/password/change", status_code=303)
                response.set_cookie(
                    key="access_token",
                    value=access_token,
                    httponly=True,
                    secure=True,
                    samesite="strict"
                )
                return response
            access_token = create_access_token(
                user_data={
                    "username": user.first_name,
                    "user_id": str(user.id),
                    "role": user.role,
                }
            )

            refresh_token = create_access_token(
                user_data={"username": user.first_name,
                           "user_id": str(user.id)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            # Update the user's last login time and tokens to the database
            user.last_login = datetime.now()
            user.token = access_token
            user.reset_token = refresh_token
            session.add(user)
            await session.commit()
            await session.refresh(user)

            response = RedirectResponse(url="/dashboard", status_code=303)
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="strict"
            )
            return response
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid login credentials")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid login credentials")


@auth_router.post("/password/change")
async def change_user_password(request: Request, password_data: PasswordChangeModel, session: AsyncSession = Depends(get_session)):
    old_password = password_data.oldPassword
    new_password = password_data.newPassword
    confirm_password = password_data.confirmPassword

    # Check if user exists
    if not request.state.user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid user session")
    # Check if new password and its confirmation matches
    if not new_password == confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    user = await user_services.get_user_by_uid(request.state.user["user"]["user_id"], session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

    # Check if old password is valid
    password_valid = verify_password(old_password, user.password_hash)
    if password_valid:
        # update user password
        password_hash = generate_password_hash(new_password)
        user.password_hash = password_hash
        user.linked = not user.linked
        user.password_status = "Changed"
        session.add(user)
        await session.commit()
        return RedirectResponse(url="/login")

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid login credentials")


@auth_router.post("/logout")
async def logout(request: Request, response: Response, session: AsyncSession = Depends(get_session)):
    token = get_request_token(request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No tokens provided")
    try:
        token_data = decode_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Token not valid")
        # remove token from user db
        if not await user_services.remove_user_tokens(token_data["user"]["user_id"], session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User token not valid")
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie("access_token")
        return response

    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid Token")
