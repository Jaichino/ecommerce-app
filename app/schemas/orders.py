############################################
#  Request and Response models for Orders #
############################################


###################################################################################################
# Imports

from datetime import datetime
from pydantic import BaseModel, Field
from app.models.orders import OrderStatus, PaymentMethod
from app.schemas.shippers import ShipperPublic
from app.schemas.users import UserPublic

###################################################################################################


###################################################################################################
# Request Schemas

class OrderDetailCreate(BaseModel):
    product_variant_id: int
    quantity: int = Field(gt=0)

    model_config = {"extra":"forbid"}


class OrderCreate(BaseModel):
    client_id: int
    shipper_id: int | None = None
    order_status: OrderStatus
    payment_method: PaymentMethod
    order_details: list[OrderDetailCreate]

    model_config = {"extra":"forbid"}


class OrderUpdate(BaseModel):
    shipper_id: int | None = None
    order_status: OrderStatus | None = None

    model_config = {"extra":"forbid"}

###################################################################################################


###################################################################################################
# Response Schemas

class OrderInfo(BaseModel):
    order_id: int
    created_at: datetime
    status: str
    payment_method: str
    total_order: float


class OrderDetailPublic(BaseModel):
    sku: str
    product_name: str
    size: str | None
    color: str
    quantity: int
    price: float


class OrderPublic(BaseModel):
    user: UserPublic
    shipper: ShipperPublic | None = None
    order_info: OrderInfo
    order_details: list[OrderDetailPublic]

    # It will be a 4-digit random number
    shipper_token: int | None

###################################################################################################