################################
# Database models for Products #
################################


###################################################################################################
# Imports

from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from app.models.order_detail import OrderDetail

if TYPE_CHECKING:
    from app.models.orders import Order

###################################################################################################


###################################################################################################
# Models

class Products(SQLModel, table=True):
    product_id: int | None = Field(default=None, primary_key=True)
    sku: str = Field(index=True, unique=True)
    product_name: str = Field(unique=True, index=True)
    brand: str | None = Field(default=None, index=True)
    product_category_id: int | None = Field(
        foreign_key="productcategory.category_id", ondelete="SET NULL"
    )
    available: bool = True

    # Model Relationships
    variants: list['ProductVariant'] = Relationship(back_populates="prod", cascade_delete=True)
    category: 'ProductCategory' = Relationship(back_populates="products")


class ProductCategory(SQLModel, table=True):
    category_id: int | None = Field(default=None, primary_key=True)
    category: str

    # Model Relationships
    products: list['Products'] = Relationship(back_populates="category")


class ProductVariant(SQLModel, table=True):
    variant_id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(
        foreign_key="products.product_id", ondelete="CASCADE"
    )
    size: str | None = Field(default=None, index=True)
    color: str = Field(index=True)
    stock: int
    price: float

    __table_args__ = (
        UniqueConstraint("product_id", "size", "color"),
    )

    # Model Relationships
    orders: list['Order'] = Relationship(back_populates="products", link_model=OrderDetail)
    prod: Products = Relationship(back_populates="variants")
    orderdetails: list['OrderDetail'] = Relationship(back_populates="product")

###################################################################################################