from beanie.operators import Set
from fastapi import APIRouter, status, HTTPException

from schemas.user import User, UserUpdate, UserView

from .auth import UserDepends

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.get(
    path="",
    response_model=UserView,
    status_code=status.HTTP_200_OK
)
async def get_self_data(user: UserDepends) -> UserView:
    return UserView(**user.model_dump())


@router.put(
    path="",
    response_model=UserView,
    status_code=status.HTTP_201_CREATED
)
async def update_self_data(user: UserDepends, data: UserUpdate) -> UserView:
    excludes = ["original_password"]
    if data.originalPassword is None or data.password is None:
        excludes.append("password")
    elif not user.check_password(data.originalPassword):
        excludes.append("password")

    user = await user.update(Set(data.model_dump(exclude_none=True, exclude=set(excludes))))

    return UserView(**user.model_dump())


@router.get(
    path="/{user_id}",
    response_model=UserView,
    status_code=status.HTTP_200_OK,
)
async def get_user_data(user_id: str) -> UserView:
    user = await User.find_one(User.uid == user_id, projection_model=UserView)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user
