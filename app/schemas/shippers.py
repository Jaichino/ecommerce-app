############################################
# Request and Response models for Shippers #
############################################


###################################################################################################
# Imports

from pydantic import BaseModel, EmailStr

###################################################################################################


###################################################################################################
# Request Schemas

class ShipperCreate(BaseModel):
    shipper_name: str
    shipper_email: EmailStr
    shipper_phone_number: str | None = None

    model_config = {"extra":"forbid"}


class ShipperUpdate(BaseModel):
    shipper_name: str | None = None
    shipper_email: EmailStr | None = None
    shipper_phone_number: str | None = None

    model_config = {"extra":"forbid"}

###################################################################################################


###################################################################################################
# Response Schemas

class ShipperPublic(BaseModel):
    shipper_id: int
    shipper_name: str
    shipper_email: str
    shipper_phone_number: str | None

###################################################################################################