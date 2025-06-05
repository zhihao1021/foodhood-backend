from pydantic import BaseModel, Field, field_validator

from datetime import datetime, timedelta
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc

from snowflake import SnowflakeID


class JWT(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class JWTPayload(BaseModel):
    sub: SnowflakeID
    iat: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        examples=[1737170068]
    )
    exp: datetime = Field(
        default_factory=lambda: datetime.now(UTC) + timedelta(days=7),
        examples=[1737774868]
    )
    is_admin: bool = Field(
        default=False,
        title="Is Admin",
        description="Whether the user is admin.",
        examples=[True],
    )

    @field_validator("exp", "iat", mode="before")
    @classmethod
    def valid_exp(cls, value):
        if isinstance(value, datetime):
            return value

        try:
            return datetime.fromtimestamp(value, tz=UTC)
        except:
            raise ValueError

    @field_validator("sub", mode="before")
    @classmethod
    def valid_sub(cls, value):
        if isinstance(value, SnowflakeID):
            return value

        try:
            return SnowflakeID(value)
        except:
            raise ValueError
