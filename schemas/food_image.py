from beanie import Document

from snowflake import SnowflakeID


class FoodImage(Document):
    food_id: SnowflakeID
    index: int
    content_type: str
    data: bytes

    class Settings:
        name = "FoodImages"
        bson_encoders = {
            SnowflakeID: str
        }
