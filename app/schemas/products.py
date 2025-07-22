############################################
# Request and Response models for Products #
############################################


###################################################################################################
# Imports

from pydantic import BaseModel, Field

###################################################################################################


###################################################################################################
# Request Schemas

class ProductBaseCreate(BaseModel):
    sku: str
    product_name: str
    category_id: int | None = None

    model_config = {"extra": "forbid"}


class ProductVariantCreate(BaseModel):
    product_id: int
    size: str | None = Field(max_length=4)
    color: str
    quantity: int
    price: float

    model_config = {"extra": "forbid"}


class CategoryCreate(BaseModel):
    category: str

    model_config = {"extra": "forbid"}


class ProductUpdate(BaseModel):
    sku: str | None = None
    product_name: str | None = None
    product_category_id: int | None = None
    available: bool | None = None

    model_config = {"extra": "forbid"}


class ProductVariantUpdate(BaseModel):
    size: str | None = None
    color: str | None = None
    stock: int | None = None
    price: float | None = None

    model_config = {"extra": "forbid"}

###################################################################################################


###################################################################################################
# Response Schemas

class ProductVariantPublic(BaseModel):
    variant_id: int
    product_name: str
    size: str | None
    color: str
    stock: int
    price: float


class CategoryPublic(BaseModel):
    category_id: int
    category_name: str


class ProductBasePublic(BaseModel):
    product_id: int
    sku: str
    product_name: str
    product_category: str
    available: bool
    product_variants: list[ProductVariantPublic] | None

###################################################################################################