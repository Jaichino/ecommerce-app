############################################
#   Request and Response models for Carts  #
############################################


###################################################################################################
# Imports

from pydantic import BaseModel, Field

###################################################################################################


###################################################################################################
# Request Schemas

class CartDetailCreate(BaseModel):
    product_variant_id: int
    quantity: int = Field(gt=0)

    model_config = {"extra":"forbid"}


class CartCreate(BaseModel):
    client_id: int
    cart_detail: list[CartDetailCreate]

    model_config = {"extra":"forbid"}

###################################################################################################


###################################################################################################
# Response Schemas

class CartDetailPublic(BaseModel):
    product_variant_id: int
    product_name: str
    quantity: int
    price: float


class CartPublic(BaseModel):
    cart_id: int
    client_id: int
    cart_detail: list[CartDetailPublic]
    total_price: float

###################################################################################################