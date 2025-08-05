##################################
# API Router for Products module #
##################################


###################################################################################################
# Imports

from typing import Annotated
from sqlmodel import Session
from fastapi import APIRouter, Depends, status, Body

from app.db.database import get_session



from app.schemas.products import (
    ProductBaseCreate, ProductBasePublic, ProductVariantPublic, ProductVariantCreate,
    ProductUpdate, FullProductPublic, CategoryCreate, CategoryPublic, CategoryUpdate
)

from app.crud.products import ProductCrud

###################################################################################################


###################################################################################################
# Router configuration

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

###################################################################################################
# Session dependency

SessionDep = Annotated[Session, Depends(get_session)]

###################################################################################################


###################################################################################################
# POST ENDPOINTS

###################################################################################################
# Create new base products
@router.post(
        "",
        response_model=ProductBasePublic,
        status_code=status.HTTP_201_CREATED,
        responses={
            status.HTTP_201_CREATED:{
                "description": "Created",
                "content": {
                    "application/json": {
                        "example": {
                            "product_id": 1,
                            "sku": "SH0001",
                            "product_name": "Black cotton shirt",
                            "brand": "Lacoste",
                            "product_category_id": 1,
                            "available": True
                        }
                    }
                }
            },
            status.HTTP_404_NOT_FOUND:{
                "description": "Not Found",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Category with category_id '544' not found!"
                        }
                    }
                }
            }
        }
)
async def create_base_product(
    session: SessionDep,
    product: Annotated[
        ProductBaseCreate, 
        Body(example={
                "sku": "SH0001",
                "product_name": "Black cotton shirt",
                "brand": "Lacoste",
                "product_category_id": 1
            }
        )
    ]
) -> ProductBasePublic:
    
    """
    Creates a new base product by passing a JSON object with fields like sku, product name,
    brand and category.
    """

    # Creates the product
    created_product = ProductCrud.create_product_base(session=session, product_in=product)

    # Return the product
    return created_product
###################################################################################################

###################################################################################################
# Create a new product variant
@router.post(
    "/{sku}/variants",
    summary="Creates a new product variant",
    response_model=ProductVariantPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Created",
            "content": {
                "application/json":{
                    "example":{
                        "variant_id": 2,
                        "product_id": 5,
                        "size": "L",
                        "color": "Black",
                        "stock": 5,
                        "price": 86000.0
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND:{
            "description": "Not Found",
            "content":{
                "application/json":{
                    "example":{
                        "detail": "Product with sku '5' not found!"
                    }
                }
            }
        }
    }
)
async def create_product_variant(
    session: SessionDep,
    sku: str,
    variant_create: Annotated[
        ProductVariantCreate,
        Body(example={
            "size": "L",
            "color": "Black",
            "quantity": 5,
            "price": 86000
        })
    ]
):
    """
    Creates a new product variant by passing product data like size, color, quantity and price.
    If the variant already exists, then the quantity and price are updated.

    - **sku**: The product's sku code.
    """

    # Create and return the product variant
    product_variant = ProductCrud.create_product_variant(
        session=session,
        sku=sku,
        product_variant=variant_create
    )

    return product_variant
###################################################################################################

###################################################################################################

###################################################################################################
# GET ENDPOINTS

###################################################################################################
# Get one product
@router.get(
    "/{sku}",
    response_model=FullProductPublic,
    responses={
        status.HTTP_200_OK:{
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {
                        "product_id": 5,
                        "sku": "SH0001",
                        "product_name": "Cotton shirt",
                        "brand": "Lacoste",
                        "product_category": "Shirts",
                        "available": True,
                        "product_variants": [
                            {
                                "variant_id": 2,
                                "product_id": 5,
                                "size": "L",
                                "color": "Black",
                                "stock": 13,
                                "price": 90000.0
                            },
                            {
                                "variant_id": 10,
                                "product_id": 5,
                                "size": "L",
                                "color": "Blue",
                                "stock": 4,
                                "price": 87000.0
                            }
                        ]
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Product with sku 'ZS10220' not found!"
                    }
                }
            }
        }
    }
)
async def get_product_by_sku(session: SessionDep, sku: str) -> FullProductPublic:
    """
    Gets a product with its full information like name, brand, category and variants.

    - **sku**: The product's sku.
    """

    # Get the product
    product = ProductCrud.get_full_product_by_sku(session, sku)

    # Return the product
    return product

###################################################################################################