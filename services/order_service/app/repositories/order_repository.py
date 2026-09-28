import asyncio
from datetime import datetime
from uuid import UUID
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order as OrderModel
from app.schemas.order import OrderCreate, OrderUpdate


class OrderRepository:
    async def get_all_orders(self, db: AsyncSession, *, status: Optional[str], skip: int, limit: int) -> list[OrderModel]:
        stmt = select(OrderModel).options(selectinload(OrderModel.order_items))
        if status:
            stmt = stmt.filter(OrderModel.status == status)
        stmt = stmt.order_by(OrderModel.created_at).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_order_by_id(self, db: AsyncSession, *, order_id: UUID) -> Optional[OrderModel]:
        stmt = select(OrderModel).where(OrderModel.id == order_id).options(selectinload(OrderModel.order_items))
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_orders_by_user_id(self, db: AsyncSession, *, user_id: UUID) -> list[OrderModel]:
        stmt = select(OrderModel).where(OrderModel.user_id == user_id).options(selectinload(OrderModel.order_items))
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_order(self, db: AsyncSession, *, obj_in: OrderCreate) -> OrderModel:
        order = OrderModel(**obj_in.model_dump())
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    async def update_order(self, db: AsyncSession, *, order_id: UUID, obj_in: OrderUpdate) -> OrderModel:
        order = await self.get_order_by_id(db, order_id=order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        for attr, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(order, attr, value)

        await db.commit()
        await db.refresh(order)
        return order

    async def delete_order(self, db: AsyncSession, *, order_id: UUID) -> OrderModel | None:
        order = await self.get_order_by_id(db, order_id=order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        await db.delete(order)
        await db.commit()
        return order


order_repository = OrderRepository()