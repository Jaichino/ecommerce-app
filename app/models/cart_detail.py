######################################
#   Database models for Cart Detail  #
######################################


###################################################################################################
# Imports

from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint


if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.products import ProductVariant

###################################################################################################


###################################################################################################
# Models

class CartDetail(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    cart_id: int = Field(
        foreign_key="cart.id", ondelete="CASCADE"
    )
    product_id: int = Field(
        foreign_key="productvariant.variant_id", ondelete="CASCADE"
    )
    quantity: int
    subtotal: float

    __table_args__ = (
        UniqueConstraint("cart_id", "product_id"),
    )

    # Model Relationships
    cart: 'Cart' = Relationship(back_populates="detail")
    product: 'ProductVariant' = Relationship(back_populates="cartdetails")

####################################################################################################