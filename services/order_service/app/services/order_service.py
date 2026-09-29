from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from uuid import UUID
from typing import Optional
from app.models.order import Order as OrderModel
from app.schemas.order import OrderCreate, OrderUpdate

from app.repositories.order_repository import order_repository
from app.clients.user_service_client import user_service_client
from app.clients.notification_service_client import notification_service_client
import logging


logger = logging.getLogger(__name__)

class OrderService:
    async def get_all_orders(self, db: AsyncSession, *, status: Optional[str], skip: int, limit: int) -> list[OrderModel]:
        orders = await order_repository.get_all_orders(db, status=status, skip=skip, limit=limit)
        if not orders:
            return []
        return orders

    async def get_order_by_id(self, db: AsyncSession, *, order_id: UUID) -> Optional[OrderModel]:
        return await order_repository.get_order_by_id(db, order_id=order_id)

    async def get_orders_by_user_id(self, db: AsyncSession, *, user_id: UUID) -> list[OrderModel]:
        return await order_repository.get_orders_by_user_id(db, user_id=user_id)
    async def create_order(self, db: AsyncSession, *, obj_in: OrderCreate) -> OrderModel:
        user = await user_service_client.get_user(obj_in.user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        order = await order_repository.create_order(db, obj_in=obj_in)
        queued = await notification_service_client.enqueue_order_confirmation(
            order_id=order.id,
            user=user,
        )
        if not queued:
            logger.warning(
                "order %s was created but its confirmation notification was not queued",
                order.id,
            )
        return order

    async def update_order(self, db: AsyncSession, *, order_id: UUID, obj_in: OrderUpdate) -> OrderModel:
        return await order_repository.update_order(db, order_id=order_id, obj_in=obj_in)

    async def delete_order(self, db: AsyncSession, *, order_id: UUID) -> OrderModel | None:
        return await order_repository.delete_order(db, order_id=order_id)


order_service = OrderService()