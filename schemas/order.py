from beanie import Document, Indexed
from pydantic import (
    BaseModel,
    Field,
)

from typing import Annotated, Optional

from config import INSTANCE_ID
from snowflake import SnowflakeGenerator, SnowflakeID

uid_generator = SnowflakeGenerator(INSTANCE_ID)


class Order(Document):
    uid: Annotated[SnowflakeID, Indexed(unique=True)] = Field(
        title="UID",
        description="UID of order, use snowflake format.",
        default_factory=uid_generator.next_id,
        examples=["6209533852516352"]
    )
    foodId: SnowflakeID = Field(
        title="Food ID",
        description="UID of food, use snowflake format.",
        examples=["6209533852516352"]
    )
    userId: SnowflakeID = Field(
        title="User ID",
        description="UID of user, use snowflake format.",
        examples=["6209533852516352"]
    )
    received: bool = Field(
        title="Received",
        description="Whether the order has been received.",
        default=False,
        examples=[True, False]
    )
    complete: bool = Field(
        title="Complete",
        description="Whether the order has been completed.",
        default=False,
        examples=[True, False]
    )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        return self.uid == value.uid

    class Settings:
        name = "Orders"
        bson_encoders = {
            SnowflakeID: str
        }


class OrderUpdate(BaseModel):
    received: Optional[bool] = None
    complete: Optional[bool] = None


class OrderView(BaseModel):
    uid: Annotated[SnowflakeID, Indexed(unique=True)]
    foodId: SnowflakeID
    userId: SnowflakeID
    received: bool
    complete: bool
