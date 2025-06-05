from bcrypt import checkpw, gensalt, hashpw
from beanie import Document, Indexed
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
)

from typing import (
    Annotated,
    Optional,
)

from config import INSTANCE_ID
from snowflake import SnowflakeGenerator, SnowflakeID
from utils.email_checker import check_is_email

uid_generator = SnowflakeGenerator(INSTANCE_ID)


class User(Document):
    uid: Annotated[SnowflakeID, Indexed(unique=True)] = Field(
        title="UID",
        description="UID of user, use snowflake format.",
        default_factory=uid_generator.next_id,
        examples=["6209533852516352"]
    )
    email: Annotated[str, Indexed(unique=True)] = Field(
        title="Email",
        description="User's email.",
        examples=["user@example.com"],
    )
    username: str = Field(
        title="Username",
        description="Username of user.",
        examples=["username"],
        min_length=1
    )
    phone: str = Field(
        title="Phone number",
        description="User's phone number.",
        examples=["0912345678"],
    )
    password: bytes = Field(
        title="Password(Hash)",
        description="Password of user after hash.",
        examples=[b"passw0rd"],
    )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        return self.uid == value.uid

    def check_password(self, password: str) -> bool:
        return checkpw(password.encode("utf-8"), self.password)

    class Settings:
        name = "Users"
        bson_encoders = {
            SnowflakeID: str
        }
        max_nesting_depth = 1


class UserCreate(BaseModel):
    email: str
    username: str = Field(min_length=1)
    phone: str
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def email_must_be_email(cls, value: str) -> str:
        if not check_is_email(value):
            raise ValueError
        return value

    @field_serializer("password")
    def password_auto_hash(self, value: str) -> Optional[bytes]:
        if value:
            return hashpw(value.encode("utf-8"), gensalt())
        return None


class UserUpdate(BaseModel):
    email: Optional[str] = Field(None, min_length=1)
    username: Optional[str] = Field(None, min_length=1)
    phone: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)
    originalPassword: Optional[str] = None

    @field_serializer("password")
    def password_auto_hash(self, value: str) -> Optional[bytes]:
        if value:
            return hashpw(value.encode("utf-8"), gensalt())
        return None

class UserView(BaseModel):
    uid: SnowflakeID
    email: str
    username: str
    phone: str
    