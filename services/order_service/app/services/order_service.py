from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import Optional
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderUpdate, Order

from app.repositories.order_repository import order_repository

class OrderService:
    async def get_all_orders(self, db: AsyncSession, *, status: Optional[str], skip: int, limit: int) -> list[Order]:
        orders = await order_repository.get_all_orders(db, status=status, skip=skip, limit=limit)
        if not orders:
            return []
        return orders

    async def get_order_by_id(self, db: AsyncSession, *, order_id: UUID) -> Optional[Order]:
        return await order_repository.get_order_by_id(db, order_id=order_id)

    async def get_orders_by_user_id(self, db: AsyncSession, *, user_id: UUID) -> list[Order]:
        return await order_repository.get_orders_by_user_id(db, user_id=user_id)
    async def create_order(self, db: AsyncSession, *, obj_in: OrderCreate) -> Order:
        return await order_repository.create_order(db, obj_in=obj_in)

    async def update_order(self, db: AsyncSession, *, order_id: UUID, obj_in: OrderUpdate) -> Order:
        return await order_repository.update_order(db, order_id=order_id, obj_in=obj_in)

    async def delete_order(self, db: AsyncSession, *, order_id: UUID) -> Order | None:
        return await order_repository.delete_order(db, order_id=order_id)


order_service = OrderService()