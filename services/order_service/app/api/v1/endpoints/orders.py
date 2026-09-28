from uuid import UUID

from fastapi import APIRouter, status, HTTPException, Query
from app.core.database import DBSession 
from typing import Optional
from app.schemas.order import Order, OrderCreate, OrderUpdate
from app.services.order_service import order_service
from app.api.deps import CurrentUser, TokenUser

router = APIRouter()


def _is_admin(user: TokenUser) -> bool:
    return any(role.lower() in {"admin", "superuser"} for role in user.roles)


def _require_admin(user: TokenUser) -> None:
    if not _is_admin(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")

@router.get("/", response_model=list[Order], status_code=status.HTTP_200_OK)
async def get_orders(
    db: DBSession,
    current_user: CurrentUser,
    status: Optional[str] = Query(default=None, enum=["pending", "processing", "completed", "cancelled"]),
    skip: int = 0,
    limit: int = 10,
):
    _require_admin(current_user)
    orders = await order_service.get_all_orders(db, status=status, skip=skip, limit=limit)

    return orders

@router.get("/{order_id}", response_model=Order, status_code=status.HTTP_200_OK)
async def get_order_by_id(
    db: DBSession,
    order_id: UUID,
    current_user: CurrentUser,
    ):
    order = await order_service.get_order_by_id(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.user_id != current_user.id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this order")
    return order

@router.get("/users/{user_id}", response_model=list[Order], status_code=status.HTTP_200_OK)
async def get_orders_by_user_id(
    db: DBSession,
    user_id: UUID,
    current_user: CurrentUser,
    ):
    if user_id != current_user.id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access these orders")
    orders = await order_service.get_orders_by_user_id(db, user_id=user_id)

    return orders

@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(db: DBSession, order: OrderCreate, current_user: CurrentUser):
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Orders can only be created for the authenticated user")
    return await order_service.create_order(db, obj_in=order)

@router.patch("/{order_id}", response_model=Order, status_code=status.HTTP_200_OK)
async def update_order(
    db: DBSession,
    order_id: UUID,
    order: OrderUpdate,
    current_user: CurrentUser,
    ):
    existing_order = await order_service.get_order_by_id(db, order_id=order_id)
    if existing_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if existing_order.user_id != current_user.id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update this order")
    return await order_service.update_order(db, order_id=order_id, obj_in=order)

@router.delete("/{order_id}", response_model=Order, status_code=status.HTTP_200_OK)
async def delete_order(
    db: DBSession,
    order_id: UUID,
    current_user: CurrentUser,
    ):
    existing_order = await order_service.get_order_by_id(db, order_id=order_id)
    if existing_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if existing_order.user_id != current_user.id and not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete this order")
    return await order_service.delete_order(db, order_id=order_id)