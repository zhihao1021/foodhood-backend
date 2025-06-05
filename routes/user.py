from beanie.operators import Set
from fastapi import APIRouter, status

from schemas.user import UserUpdate, UserView

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
