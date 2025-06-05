from fastapi import APIRouter, Body, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import encode, decode
from pydantic import BaseModel, Field

from typing import Annotated, Optional

from config import JWT_KEY
from schemas.jwt import JWT, JWTPayload
from schemas.user import User, UserCreate
from snowflake import SnowflakeID
from utils.email_checker import check_is_email


class LoginData(BaseModel):
    email: str = Field(
        title="Email",
        description="User's account",
        examples=["user@example.com"]
    )
    password: str = Field(
        title="Password",
        description="Login password",
        examples=["passw0rd"]
    )
    # valid_code: str


AUTHORIZE_FAILED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Authorize failed"
)
ACCOUNT_ALREADY_EXIST = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The account is already exist"
)
ACCOUNT_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Account not found"
)
INVALIDE_AUTHENTICATION_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials"
)
INVALIDE_EMAIL_ADDRESS = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid email address"
)

SECURITY = HTTPBearer(
    scheme_name="JWT",
    description="JWT which get from posting discord oauth code to /auth/login.",
    auto_error=False,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authorization"]
)

last_password_change_utc = {}


def generate_jwt(user: User) -> JWT:
    payload = JWTPayload(
        sub=user.uid,
    ).model_dump()
    token = encode(
        payload=payload,
        key=JWT_KEY,
        algorithm="HS256",
    )

    return JWT(access_token=token)


def parse_token(optional: bool = False):
    async def wrap(token: HTTPAuthorizationCredentials = Security(SECURITY)) -> Optional[JWTPayload]:
        if optional and token is None:
            return None

        try:
            jwt = token.credentials
            decode_data = JWTPayload(**decode(
                jwt=jwt,
                key=JWT_KEY,
                algorithms=["HS256"],
                options={
                    "require": ["exp", "iat", "sub"]
                }
            ))

            last_change = last_password_change_utc.get(decode_data.sub)
            if last_change is not None and decode_data.iat < last_change:
                raise INVALIDE_AUTHENTICATION_CREDENTIALS

            return decode_data
        except:
            import traceback
            traceback.print_exc()
            raise INVALIDE_AUTHENTICATION_CREDENTIALS
    return wrap


valid_token = parse_token()


async def get_uid(decode_data: Annotated[JWTPayload, Depends(valid_token)]) -> SnowflakeID:
    return decode_data.sub

uid_depends = Depends(get_uid)
UIDDepends = Annotated[SnowflakeID, uid_depends]


async def check_is_admin(decode_data: Annotated[JWTPayload, Depends(valid_token)]) -> None:
    if not decode_data.is_admin:
        raise INVALIDE_AUTHENTICATION_CREDENTIALS

AdminDepends = Depends(check_is_admin)


async def get_is_admin(
    decode_data: Annotated[Optional[JWTPayload],
                           Depends(parse_token(optional=True))]
) -> bool:
    if decode_data is None:
        return False
    return decode_data.is_admin
IsAdminDepends = Annotated[bool, Depends(get_is_admin)]


async def get_user(uid: UIDDepends) -> User:
    user = await User.find_one(User.uid == uid)
    if user is None:
        raise INVALIDE_AUTHENTICATION_CREDENTIALS

    return user

user_depends = Depends(get_user)
UserDepends = Annotated[User, user_depends]


@router.post(
    path="/login",
    response_model=JWT,
    description="Login by account and password.",
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "The acocount or password are wrong."
        },
    }
)
async def login(data: LoginData) -> JWT:
    email = data.email
    password = data.password

    user = await User.find_one(User.email == email)

    if user is None:
        raise AUTHORIZE_FAILED

    if not user.check_password(password):
        raise AUTHORIZE_FAILED

    return generate_jwt(user)


@router.post(
    path="/register",
    response_model=JWT,
    description="Register a new account and login.",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": "The account is already exist."
        }
    }
)
async def register(data: UserCreate) -> JWT:
    if await User.find_one(User.email == data.email):
        raise ACCOUNT_ALREADY_EXIST

    new_user = User(**data.model_dump())

    await User.insert_one(new_user)

    return generate_jwt(new_user)


@router.post(
    path="/check",
    status_code=status.HTTP_200_OK,
)
async def check_exist(email: Annotated[str, Body(embed=True)]) -> None:
    if not check_is_email(email):
        raise INVALIDE_EMAIL_ADDRESS

    if await User.find_one(User.email == email).exists():
        return
    raise ACCOUNT_NOT_FOUND


@router.put(
    path="/refresh",
    response_model=JWT,
    description="Update token.",
    status_code=status.HTTP_200_OK
)
def refresh_token(user: UserDepends) -> JWT:
    return generate_jwt(user)
