from fastapi import APIRouter, HTTPException, Response, status, UploadFile
from PIL import Image, ImageOps

from io import BytesIO

from schemas.food import Food, FoodCreate, FoodView
from schemas.food_image import FoodImage
from schemas.order import Order, OrderView
from snowflake import SnowflakeID

from .auth import UIDDepends

FOOD_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Food not found"
)
FOOD_FULL = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Food is full"
)
NOT_ACQUIRE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="You have not acquired this food"
)
ALREADY_ACQUIRED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Already acquired this food"
)
ALREADY_FINISHED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Already finished this food"
)
FILE_TOO_LARGE = HTTPException(
    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    detail="File size exceeds 10MB limit"
)
NO_FILE_SIZE = HTTPException(
    status_code=status.HTTP_411_LENGTH_REQUIRED,
    detail="File size is required"
)
UNSUPPORTED_MEDIA_TYPE = HTTPException(
    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    detail="Unsupported media type"
)

router = APIRouter(
    prefix="/food",
    tags=["Food"]
)


@router.get(
    path="",
    response_model=list[FoodView],
    status_code=status.HTTP_200_OK
)
async def get_food_list() -> list[FoodView]:
    return await Food.find(
        projection_model=FoodView,
    ).to_list()


@router.post(
    path="",
    response_model=FoodView,
    status_code=status.HTTP_201_CREATED,
)
async def create_food(data: FoodCreate, uid: UIDDepends) -> FoodView:
    food = Food(**data.model_dump(), authorId=uid)
    food = await food.save()
    return FoodView(**food.model_dump())


@router.get(
    path="/{food_id}",
    response_model=FoodView,
    status_code=status.HTTP_200_OK,
)
async def get_food(
    food_id: str
) -> FoodView:
    food = await Food.find_one(Food.uid == food_id, fetch_links=True)
    if food is None:
        raise FOOD_NOT_FOUND

    return FoodView(**food.model_dump())


@router.post(
    path="/{food_id}/photos",
    status_code=status.HTTP_200_OK,
)
async def upload_food_photos(
    food_id: str,
    file: list[UploadFile]
) -> None:
    food = await Food.find_one(Food.uid == food_id, fetch_links=True)
    if food is None:
        raise FOOD_NOT_FOUND

    for f in file:
        size = f.size
        if size is None:
            raise NO_FILE_SIZE
        if size > 1024 * 1024 * 10:
            raise FILE_TOO_LARGE

        data = await f.read()
        try:
            output_bytes = BytesIO()
            with Image.open(BytesIO(data)) as img:
                img.verify()
                content_type = f.content_type or (img.format or "").lower()

            with Image.open(BytesIO(data)) as img:
                img_sdr = ImageOps.autocontrast(img)
                img_sdr.save(output_bytes, format=img.format)
            data = output_bytes.getvalue()
        except:
            continue

        image = FoodImage(
            food_id=SnowflakeID(food_id),
            index=food.imageCount,
            data=data,
            content_type=content_type,
        )
        food.imageCount += 1

        await image.save()
    await food.save()


@router.get(
    path="/{food_id}/photos/{index}",
    status_code=status.HTTP_200_OK,
)
async def get_food_photos(
    food_id: str,
    index: int,
) -> Response:
    avatar = await FoodImage.find_one(FoodImage.food_id == food_id, FoodImage.index == index)
    if avatar is None:
        raise FOOD_NOT_FOUND

    return Response(avatar.data, media_type=avatar.content_type)


@router.get(
    path="/{food_id}/order",
    response_model=OrderView,
    status_code=status.HTTP_200_OK
)
async def order_food(
    food_id: str,
    user_id: UIDDepends
) -> OrderView:
    food = await Food.find_one(Food.uid == food_id, fetch_links=True)
    if food is None:
        raise FOOD_NOT_FOUND

    order = await Order.find_one(
        Order.foodId == food_id,
        Order.userId == user_id,
    ).project(OrderView)

    if order:
        return order

    order = Order(
        foodId=SnowflakeID(food_id),
        userId=user_id,
    )
    await order.save()
    return OrderView(**order.model_dump())


@router.get(
    path="/{food_id}/status",
    response_model=list[OrderView],
    status_code=status.HTTP_200_OK,
)
async def get_food_status(
    food_id: str
) -> list[OrderView]:
    food = await Food.find_one(Food.uid == food_id)
    if food is None:
        raise FOOD_NOT_FOUND

    return await Order.find(
        Order.foodId == food_id,
        projection_model=OrderView
    ).to_list()
