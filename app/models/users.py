################################
#   Database models for Users  #
################################


###################################################################################################
# Imports

from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum

if TYPE_CHECKING:
    from app.models.orders import Order
    from app.models.shippers import Shipper

###################################################################################################


###################################################################################################
# Models

class UserRole(Enum):
    admin = "admin"
    client = "client"
    shipper = "shipper"


class User(SQLModel, table=True):
    user_id: int | None = Field(default=None, primary_key=True)
    firstname: str
    lastname: str = Field(index=True)
    user_dni: int = Field(unique=True)
    user_email: str = Field(unique=True)
    hash_password: str
    is_active: bool = True
    role: UserRole
    shipper_id: int | None = Field(foreign_key="shipper.shipper_id", ondelete="CASCADE")

    # Model Relationships
    orders: list['Order'] = Relationship(back_populates="client")
    user_address: 'UserAddress' = Relationship(back_populates="user", cascade_delete=True)
    shipper: 'Shipper' = Relationship(back_populates="users")


class UserAddress(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id", unique=True, ondelete="CASCADE")
    phone_number: str | None = Field(default=None, unique=True)
    user_address: str = Field(unique=True)
    city: str
    province: str
    is_apartment: bool | None = None
    floor: int | None = None
    apartment: str | None = None

    # Model Relationships
    user: User = Relationship(back_populates="user_address")

###################################################################################################
