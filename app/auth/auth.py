####################################
# Authentication and Authorization #
####################################

###################################################################################################
# Imports

import os
from typing import Annotated
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pathlib import Path
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.schemas.users import UserPublic
from app.crud.users import UsersCrud
from app.db.database import get_session

###################################################################################################


###################################################################################################
# User data
class TokenData(BaseModel):
    username: str
    role: str

###################################################################################################


###################################################################################################
# Security schema
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")

###################################################################################################

###################################################################################################
# Session dependency
SessionDep = Annotated[Session, Depends(get_session)]

###################################################################################################


###################################################################################################
# JWT SECRET_KEY and ALGORITHM

# Algorithm
ALGORITHM="HS256"

# Get the SECRET_KEY from .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)
SECRET_KEY = os.getenv("SECRET_KEY")
###################################################################################################


###################################################################################################
# JWT Creator

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    
    payload = data.copy()

    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    # Generate the jwt
    payload.update({"exp": expires})
    encoded_jwt = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

    # Return the jwt
    return encoded_jwt
###################################################################################################


###################################################################################################
# Get current user
def get_current_user(
        token: Annotated[str, Depends(oauth2_schema)],
        session: SessionDep
) -> UserPublic:

    # Credential exception
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials",
        headers= {"WWW-Authenticate": "Bearer"}
    )

    try:
        # Decode the token
        decoded_token = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])

        # Get the user info
        username = decoded_token.get("sub")
        role = decoded_token.get("role")

        # Raise exception if there's no username or role
        if username is None or role is None:
            raise credential_exception

        # Create a TokenData 
        token_data = TokenData(username=username, role=role)

        # Get a UserPublic and return it
        user = UsersCrud.get_user_public(session=session, user_email=token_data.username)

        return user

    except InvalidTokenError:
        raise credential_exception

###################################################################################################

###################################################################################################
# Verify that the user is active
def get_current_active_user(user: Annotated[UserPublic, Depends(get_current_user)]) -> UserPublic:

    is_active = user.is_active

    # Raise exception if the user isn't active
    if is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account!"
        )
    
    return user

###################################################################################################


###################################################################################################
# Verify the user role
def required_role(required_role: str):
    def role_checker(
            current_user: Annotated[UserPublic, Depends(get_current_active_user)]
    ) -> UserPublic:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You do not have permission to access this resource"
            )
        return current_user
    return role_checker

###################################################################################################