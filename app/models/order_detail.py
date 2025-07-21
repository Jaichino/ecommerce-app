########################################
#   Database models for Order Details  #
########################################


###################################################################################################
# Imports

from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint


if TYPE_CHECKING:
    from app.models.orders import Order
    from app.models.products import ProductVariant

###################################################################################################


###################################################################################################
# Models

class OrderDetail(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(
        foreign_key="order.order_id", ondelete="CASCADE"
    )
    product_id: int | None = Field(
        foreign_key="productvariant.variant_id", ondelete="SET NULL"
    )
    quantity: int
    price: float

    __table_args__ = (
        UniqueConstraint("order_id", "product_id"),
    )

    # Model Relationships
    order: 'Order' = Relationship(back_populates="details")
    product: 'ProductVariant' = Relationship(back_populates="orderdetails")

###################################################################################################