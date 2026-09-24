from uuid import UUID

from fastapi import APIRouter, status, HTTPException, Query
from app.core.database import DBSession 
from typing import Optional
from app.schemas.order import Order, OrderCreate, OrderUpdate
from app.services.order_service import order_service

router = APIRouter()

@router.get("/", response_model=list[Order], status_code=status.HTTP_200_OK)
async def get_orders(
    db: DBSession,
    status: Optional[str] = Query(default=None, enum=["pending", "processing", "completed", "cancelled"]),
    skip: int = 0,
    limit: int = 10
    ):
    orders = await order_service.get_all_orders(db, status=status, skip=skip, limit=limit)

    return orders

@router.get("/{order_id}", response_model=Order, status_code=status.HTTP_200_OK)
async def get_order_by_id(
    db: DBSession,
    order_id: UUID
    ):
    order = await order_service.get_order_by_id(db, order_id=order_id)

    return order

@router.get("/by-user/{user_id}", response_model=list[Order], status_code=status.HTTP_200_OK)
async def get_orders_by_user_id(
    db: DBSession,
    user_id: UUID
    ):
    orders = await order_service.get_orders_by_user_id(db, user_id=user_id)

    return orders

@router.post("/", response_model=OrderCreate, status_code=status.HTTP_201_CREATED)
async def create_order(db: DBSession, order: Order):
    return await order_service.create_order(db, obj_in=order)

@router.patch("/{order_id}", response_model=OrderUpdate, status_code=status.HTTP_200_OK)
async def update_order(
    db: DBSession,
    order_id: UUID,
    order: Order
    ):
    return await order_service.update_order(db, order_id=order_id, obj_in=order)

@router.delete("/{order_id}", response_model=Order, status_code=status.HTTP_200_OK)
async def delete_order(
    db: DBSession,
    order_id: UUID
    ):
    return await order_service.delete_order(db, order_id=order_id)