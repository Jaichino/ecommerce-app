#######################
# APIRouter for login #
#######################


###################################################################################################
# Imports

from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlmodel import Session
from app.db.database import get_session
from app.crud.users import UsersCrud
from app.auth.hashing import check_password
from app.auth.auth import create_access_token

###################################################################################################


###################################################################################################
# Router configuration

router = APIRouter(
    prefix="/login",
    tags=["Login"]
)

###################################################################################################
# Session dependency

SessionDep = Annotated[Session, Depends(get_session)]

###################################################################################################


###################################################################################################
# Token duration (minutes)

ACCESS_TOKEN_EXPIRE_MINUTES = 60

###################################################################################################


###################################################################################################
# Login endpoint
@router.post("")
async def login(
    login_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
) -> str:
    
    # Login exception
    login_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
    )
    
    # Dict to save user information
    user_data = {}

    # Get the database user with the form credentials
    database_user = UsersCrud.get_user_db(session=session, user_email=login_form.username)

    # If not user, raise exception
    if not database_user:
        raise login_exception
    
    # Check the plain password with the hashed password
    user_validate = check_password(
        plain_password=login_form.password, hashed_password=database_user.hash_password
    )

    # If the password isn't checked raise exception
    if not user_validate:
        raise login_exception
    
    # Add sub and role to user_data
    sub = database_user.user_email
    role = database_user.role

    user_data.update(
        {
            "sub": sub,
            "role": role.value
        }
    )

    # Generate an access token and return it
    access_token = create_access_token(
        data=user_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )
