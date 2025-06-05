from fastapi import APIRouter, HTTPException, status, UploadFile
from fastapi.responses import Response
from PIL import Image, ImageOps

from io import BytesIO

from schemas.avatar import Avatar

from .auth import UIDDepends

FILE_TOO_LARGE = HTTPException(
    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    detail="File size exceeds 5MB limit"
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
    prefix="/avatar",
    tags=["Avatar"]
)

with open("default_avatar.png", "rb") as default_avatar:
    default_avatar_data = default_avatar.read()


@router.get(
    path="",
    status_code=status.HTTP_200_OK,
)
async def get_avatar(uid: UIDDepends) -> Response:
    avatar = await Avatar.find_one(Avatar.uid == uid)
    if avatar is None:
        return Response(default_avatar_data, media_type="image/png")

    return Response(avatar.data, media_type=avatar.content_type)


@router.post(
    path="",
    status_code=status.HTTP_201_CREATED,
)
async def update_avatar(uid: UIDDepends, file: UploadFile) -> None:
    size = file.size
    if size is None:
        raise NO_FILE_SIZE
    if size > 1024 * 1024 * 5:
        raise FILE_TOO_LARGE

    data = await file.read()
    try:
        output_bytes = BytesIO()
        with Image.open(BytesIO(data)) as img:
            img.verify()
            content_type = file.content_type or (img.format or "").lower()

        with Image.open(BytesIO(data)) as img:
            img_sdr = ImageOps.autocontrast(img)
            img_sdr.save(output_bytes, format=img.format)
        data = output_bytes.getvalue()
    except:
        raise UNSUPPORTED_MEDIA_TYPE
    
    avatar = await Avatar.find_one(Avatar.uid == uid)
    if avatar is None:
        avatar = Avatar(
            uid=uid,
            data=data,
            content_type=content_type,
        )
    else:
        avatar.data = data
        avatar.content_type = content_type
    await avatar.save()


@router.delete(
    path="",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_avatar(uid: UIDDepends) -> None:
    await Avatar.find_one(Avatar.uid == uid).delete()


@router.get(
    path="/{uid}",
    status_code=status.HTTP_200_OK,
)
async def get_avatar_by_uid(uid: str,) -> Response:
    avatar = await Avatar.find_one(Avatar.uid == uid)
    if avatar is None:
        return Response(default_avatar_data, media_type="image/png")

    return Response(avatar.data, media_type=avatar.content_type)
