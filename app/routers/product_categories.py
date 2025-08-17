#####################################
# API Router for product categories #
#####################################


###################################################################################################
# Imports

from typing import Annotated
from sqlmodel import Session
from fastapi import APIRouter, Depends, status

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

example_list_categories = {
    "application/json":{
        "example":[
            {
                "category_id": 1,
                "category": "SHIRTS"
            },
            {
                "category_id": 3,
                "category": "T-SHIRTS"
            }
        ]
    }
}

example_one_category = {
    "application/json":{
        "example":{
            "category_id": 1,
            "category": "SHIRTS"
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
    dependencies=[Depends(required_role("admin"))],
    responses={
        status.HTTP_201_CREATED:{
            "description": "Created",
            "content": example_one_category
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

###################################################################################################


###################################################################################################
# GET ENDPOINTS

###################################################################################################
# Get the product categories
@router.get(
    "",
    response_model = list[CategoryPublic],
    dependencies=[Depends(required_role("admin"))],
    responses={
        status.HTTP_200_OK:{
            "description": "OK",
            "content": example_list_categories
        }
    }
)
async def get_product_categories(session: SessionDep):
    """
    Gets all the product categories.
    """
    # Get the categories
    categories = ProductCrud.get_categories(session=session)

    # Return the categories
    return categories
###################################################################################################

###################################################################################################


###################################################################################################
# UPDATE ENDPOINTS

###################################################################################################
# Update a category
@router.patch(
    "/{category_id}",
    response_model=CategoryPublic,
    dependencies=[Depends(required_role("admin"))],
    responses={
        status.HTTP_200_OK:{
            "description": "OK",
            "content": example_one_category
        }
    }
)
async def update_product_category(
    session: SessionDep,
    category_id: int,
    category_update: CategoryUpdate
):
    """
    Update a product category by passing its id number and the fields to be modified, like the
    category name.

    - **category_id (int)**: The id number of product category.
    - **category_update (CategoryUpdate)**: Data to modify the category.
    """

    # Update the category
    updated_category = ProductCrud.update_category(session, category_id, category_update)

    # Return the updated category
    return updated_category

###################################################################################################

###################################################################################################


###################################################################################################
# DELETE ENDPOINTS

###################################################################################################
# Delete a product category
@router.delete(
    "/{category_id}",
    response_model=CategoryPublic,
    dependencies=[Depends(required_role("admin"))],
    responses={
        status.HTTP_200_OK:{
            "description": "OK",
            "content": example_one_category
        },
        status.HTTP_404_NOT_FOUND:example_category_notfound
    }
)
async def delete_product_category(session: SessionDep, category_id: int):

    # Delete the product category
    deleted_category = ProductCrud.delete_category(session, category_id)

    # Return the deleted category
    return deleted_category
###################################################################################################


###################################################################################################