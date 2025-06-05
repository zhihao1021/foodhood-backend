from beanie import Document, Indexed

from typing import Annotated

from snowflake import SnowflakeID


class Avatar(Document):
    uid: Annotated[SnowflakeID, Indexed(unique=True)]
    content_type: str
    data: bytes

    class Settings:
        name = "Avatars"
        bson_encoders = {
            SnowflakeID: str
        }
