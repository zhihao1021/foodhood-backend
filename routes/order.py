from beanie.operators import Set
from fastapi import APIRouter, Body, HTTPException, status
from jwt import encode, decode

from datetime import datetime, timedelta
from typing import Annotated
try:
    from datetime import UTC
except ImportError:
    from datetime import timezone
    UTC = timezone.utc

from config import JWT_KEY
from schemas.order import Order, OrderUpdate, OrderView
from schemas.user import UserView

from .auth import UIDDepends

ORDER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Order not found"
)
INVALID_CODE = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid code"
)

router = APIRouter(
    prefix="/order",
    tags=["Order"]
)


@router.get(
    path="",
    response_model=list[OrderView],
    status_code=status.HTTP_200_OK,
)
async def get_my_orders(user_id: UIDDepends) -> list[OrderView]:
    return await Order.find(
        Order.userId == user_id,
        projection_model=OrderView
    ).to_list()


@router.delete(
    path="/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_order(
    order_id: str,
    user_id: UIDDepends
) -> None:
    order = await Order.find_one(Order.uid == order_id, Order.userId == user_id)
    if order is None:
        raise ORDER_NOT_FOUND

    await order.delete()


@router.put(
    path="/{order_id}",
    response_model=OrderView,
    status_code=status.HTTP_200_OK,
)
async def finish_order(
    order_id: str,
    user_id: UIDDepends,
    data: OrderUpdate
) -> OrderView:
    order = await Order.find_one(Order.uid == order_id, Order.userId == user_id)
    if order is None:
        raise ORDER_NOT_FOUND

    order = await order.update(Set(data.model_dump(exclude_none=True)))

    return OrderView(**order.model_dump())
