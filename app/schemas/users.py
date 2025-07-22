############################################
#   Request and Response models for Users  #
############################################


###################################################################################################
# Imports

from pydantic import BaseModel, Field, EmailStr
from app.models.users import UserRole

###################################################################################################


###################################################################################################
# Request Schemas

class UserCreate(BaseModel):
    firstname: str
    lastname: str
    user_dni: int
    email: EmailStr
    password: str
    role: UserRole
    shipper_id: int | None = None

    model_config = {"extra":"forbid"}


class CreateUserAddress(BaseModel):
    user_id: int
    phone_number: str | None = None
    user_address: str
    city: str
    province: str
    is_apartment: bool | None = None
    floor: int | None = None
    apartment: str | None = None

    model_config = {"extra":"forbid"}


class UserUpdate(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    password: str | None = None

    model_config = {"extra":"forbid"}


class UserAddressUpdate(BaseModel):
    phone_number: str | None = None
    user_address: str | None = None
    city: str | None = None
    province: str | None = None
    is_apartment: bool | None = None
    floor: int | None = None
    apartment: str | None = None

    model_config = {"extra":"forbid"}

###################################################################################################
# Response Schemas

class UserAddressPublic(BaseModel):
    phone_number: str | None
    user_address: str
    city: str
    province: str
    is_apartment: bool | None
    floor: int | None
    apartment: str | None


class UserPublic(BaseModel):
    user_id: int
    firstname: str
    lastname: str
    user_dni: int
    email: str
    address: UserAddressPublic | None

###################################################################################################