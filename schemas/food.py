from beanie import Document, Indexed
from pydantic import (
    BaseModel,
    Field,
)

from typing import Annotated

from config import INSTANCE_ID
from snowflake import SnowflakeGenerator, SnowflakeID

uid_generator = SnowflakeGenerator(INSTANCE_ID)


class Food(Document):
    uid: Annotated[SnowflakeID, Indexed(unique=True)] = Field(
        title="UID",
        description="UID of food, use snowflake format.",
        default_factory=uid_generator.next_id,
        examples=["6209533852516352"]
    )
    authorId: Annotated[SnowflakeID, Indexed()] = Field(
        title="Author ID",
        description="UID of author who created the food.",
        examples=["6209533852516352"]
    )
    title: str = Field(
        title="Title",
        description="Title of food.",
        examples=["Food Title"],
    )
    description: str = Field(
        title="Description",
        description="Description of food.",
        examples=["Food Description"],
    )
    includesVegetarian: bool = Field(
        title="Includes Vegetarian",
        description="Whether the food includes vegetarian options.",
        default=False,
        examples=[True, False]
    )
    needTableware: bool = Field(
        title="Need Tableware",
        description="Whether the food requires tableware.",
        default=False,
        examples=[True, False]
    )
    tags: list[int] = Field(
        title="Tags",
        description="List of tags associated with the food.",
        default_factory=list,
        examples=[[1, 2, 3]]
    )
    latitude: float = Field(
        title="Latitude",
        description="Latitude of the food location.",
        examples=[25.0330]
    )
    longitude: float = Field(
        title="Longitude",
        description="Longitude of the food location.",
        examples=[121.5654]
    )
    locationDescription: str = Field(
        title="Location Description",
        description="Description of the food location.",
        examples=["Near Taipei 101"]
    )
    validityPeriod: float = Field(
        title="Validity Period",
        description="Validity period of the food in hours.",
        examples=[1.5]
    )
    imageCount: int = Field(
        title="Image Count",
        description="Number of images associated with the food.",
        default=0,
        examples=[3]
    )
    createdAt: int = Field(
        title="Created At",
        description="Timestamp of when the food was created.",
        examples=[1633036800]
    )

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        return self.uid == value.uid

    class Settings:
        name = "Foods"
        bson_encoders = {
            SnowflakeID: str
        }
        max_nesting_depth = 1


class FoodCreate(BaseModel):
    title: str
    description: str
    includesVegetarian: bool
    needTableware: bool
    tags: list[int]
    latitude: float
    longitude: float
    locationDescription: str
    validityPeriod: float
    createdAt: int


# class FoodUpdate(BaseModel):
#     title: Optional[str] = None
#     description: Optional[str] = None
#     points: Optional[int] = None
#     total_count: Optional[int] = None
#     level: Optional[int] = None
#     display: Optional[bool] = None
#     release_date: Optional[int] = None
#     time_limit: Optional[int] = None
#     method: Optional[str] = None
#     link: Optional[str] = None

#     @field_serializer("release_date")
#     def valid_release_date(self, release_date: int):
#         return datetime.fromtimestamp(release_date)


class FoodView(BaseModel):
    uid: SnowflakeID
    authorId: str
    title: str
    description: str
    includesVegetarian: bool
    needTableware: bool
    tags: list[int]
    latitude: float
    longitude: float
    locationDescription: str
    validityPeriod: float
    imageCount: int
    createdAt: int
