#####################################
# API Router for product categories #
#####################################


###################################################################################################
# Imports

from typing import Annotated
from sqlmodel import Session
from fastapi import APIRouter, Depends, status, Body, Query

from app.db.database import get_session

from app.schemas.products import (
    CategoryCreate, CategoryPublic, CategoryUpdate
)

from app.crud.products import ProductCrud

from app.auth.auth import required_role

###################################################################################################


###################################################################################################
# Router configuration

router = APIRouter(
    prefix="/categories",
    tags=["Product categories"]
)

###################################################################################################
# Session dependency

SessionDep = Annotated[Session, Depends(get_session)]

###################################################################################################

###################################################################################################
# Responses examples

example_category_notfound = {
                "description": "Not Found",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Category with category_id '544' not found!"
                        }
                    }
                }
}

###################################################################################################

###################################################################################################
# POST ENDPOINTS

###################################################################################################
# Create a new product category
@router.post(
    "",
    response_model=CategoryPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED:{
            "description": "Created",
            "content":{
                "application/json":{
                    "example":{
                        "category_id": 1,
                        "category": "SHIRTS"
                    }
                }
            }
        }
    }
)
async def create_product_category(session: SessionDep, category: CategoryCreate):
    """
    Create a new product category by passing the name of the category.

    - **category (CategoryCreate)**: JSON object with the name of the category
    """

    # Create the category
    product_category = ProductCrud.create_product_category(session, category)

    # Return the created category
    return product_category

###################################################################################################