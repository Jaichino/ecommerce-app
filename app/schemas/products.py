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
    brand: str
    product_category_id: int | None = None

    model_config = {"extra": "forbid"}


class ProductVariantCreate(BaseModel):
    size: str | None = Field(max_length=4)
    color: str
    quantity: int
    price: float

    model_config = {"extra": "forbid"}


class CategoryCreate(BaseModel):
    category: str

    model_config = {"extra": "forbid"}


class ProductUpdate(BaseModel):
    product_name: str | None = None
    brand: str
    product_category_id: int | None = None
    available: bool | None = None

    model_config = {"extra": "forbid"}


class CategoryUpdate(BaseModel):
    category: str | None = None

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

class ProductBasePublic(BaseModel):
    product_id: int
    sku: str
    product_name: str
    brand: str
    product_category_id: int
    available: bool


class ProductVariantPublic(BaseModel):
    variant_id: int
    product_id: int
    size: str | None
    color: str
    stock: int
    price: float


class CategoryPublic(BaseModel):
    category_id: int
    category: str


class FullProductPublic(BaseModel):
    product_id: int
    sku: str
    product_name: str
    brand: str
    product_category: str
    available: bool
    product_variants: list[ProductVariantPublic] | None

###################################################################################################