import asyncio
from datetime import datetime
from uuid import UUID
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem
from app.schemas.order import Order, OrderCreate, OrderUpdate


class OrderRepository:
    async def get_all_orders(self, db: AsyncSession, *, status: Optional[str], skip: int, limit: int) -> list[Order]:
        stmt = select(Order).options(selectinload(Order.order_items))
        if status:
            stmt = stmt.filter(Order.status == status)
        stmt = stmt.order_by(Order.created_at).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_order_by_id(self, db: AsyncSession, *, order_id: UUID) -> Optional[Order]:
        stmt = select(Order).where(Order.id == order_id).options(selectinload(Order.order_items))
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_orders_by_user_id(self, db: AsyncSession, *, user_id: UUID) -> list[Order]:
        stmt = select(Order).where(Order.user_id == user_id).options(selectinload(Order.order_items))
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_order(self, db: AsyncSession, *, obj_in: OrderCreate) -> Order:
        order = Order(**obj_in.dict())
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    async def update_order(self, db: AsyncSession, *, order_id: UUID, obj_in: OrderUpdate) -> Order:
        order = await self.get_order_by_id(db, order_id=order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        for attr, value in obj_in.dict(exclude_unset=True).items():
            setattr(order, attr, value)

        await db.commit()
        await db.refresh(order)
        return order

    async def delete_order(self, db: AsyncSession, *, order_id: UUID) -> Order | None:
        order = await self.get_order_by_id(db, order_id=order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        await db.delete(order)
        await db.commit()
        return order


order_repository = OrderRepository()