################################
#  Database models for Orders  #
################################


###################################################################################################
# Imports

from typing import TYPE_CHECKING
from datetime import timezone, datetime
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from app.models.order_detail import OrderDetail

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.shippers import Shipper
    from app.models.products import ProductVariant

###################################################################################################


###################################################################################################
# Models

class OrderStatus(Enum):
    pending = "pending"
    confirmed = "confirmed"
    shipped = "shipped"
    delivered = "delivered"
    canceled = "canceled"


class PaymentMethod(Enum):
    credit_card = "credit card"
    debit_card = "debit card"
    transfer = "bank transfer"
    cash = "cash"


class Order(SQLModel, table=True):
    order_id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    client_id: int | None = Field(
        foreign_key="user.user_id", ondelete="SET NULL"
    )
    shipper_id: int | None = Field(
        foreign_key="shipper.shipper_id", ondelete="SET NULL"
    )
    order_status: OrderStatus
    payment_method: PaymentMethod
    total_order: float
    shipper_token: int | None = None

    # Model Relationships
    client: 'User' = Relationship(back_populates="orders")
    products: list['ProductVariant'] = Relationship(
        back_populates="orders", link_model=OrderDetail
    )
    shipper: 'Shipper' = Relationship(back_populates="orders_shipper")
    details: list['OrderDetail'] = Relationship(back_populates="order", cascade_delete=True)

###################################################################################################