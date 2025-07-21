################################
# Database models for Shippers #
################################


###################################################################################################
# Imports

from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.orders import Order
    from app.models.users import User

###################################################################################################


###################################################################################################
# Models

class Shipper(SQLModel, table=True):
    shipper_id: int | None = Field(default=None, primary_key=True)
    shipper_name: str
    shipper_email: str
    shipper_contact: str | None = None

    # Model Relationships
    orders_shipper: list['Order'] = Relationship(back_populates="shipper")
    users: list['User'] = Relationship(back_populates="shipper", cascade_delete=True)

###################################################################################################