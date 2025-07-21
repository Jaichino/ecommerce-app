################################
#   Database models for Cart   #
################################


###################################################################################################
# Imports

from typing import TYPE_CHECKING
from datetime import timezone, datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.cart_detail import CartDetail

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.products import ProductVariant

###################################################################################################


###################################################################################################
# Models

class Cart(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="user.user_id", ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Model Relationships
    user: 'User' = Relationship(back_populates="user_cart")
    products: list['ProductVariant'] = Relationship(back_populates="carts", link_model=CartDetail)
    detail: list['CartDetail'] = Relationship(back_populates="cart", cascade_delete=True)

###################################################################################################