##################################
# API Router for Products module #
##################################


###################################################################################################
# Imports

from typing import Annotated
from sqlmodel import Session
from fastapi import APIRouter, Depends, status, Body, Query

from app.db.database import get_session

from app.schemas.products import (
    ProductBaseCreate, ProductBasePublic, ProductVariantPublic, ProductVariantCreate,
    ProductUpdate, FullProductPublic, ProductVariantUpdate
)

from app.crud.products import ProductCrud

from app.auth.auth import required_role

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
# Responses examples

example_variant_notfound = {
            "description": "Not Found",
            "content": {
                "application/json":{
                    "example":{
                        "detail": "Variant with variant_id '206' not found!"
                    }
                }
            }
}

example_sku_notfound = {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Product with sku 'ZS10220' not found!"
                    }
                }
            }
}

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
# POST ENDPOINTS

###################################################################################################
# Create new base products
@router.post(
        "",
        response_model=ProductBasePublic,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(required_role("admin"))],
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
            status.HTTP_404_NOT_FOUND: example_category_notfound
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
    dependencies=[Depends(required_role("admin"))],
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
        status.HTTP_404_NOT_FOUND: example_sku_notfound
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
# Get a list of products
@router.get(
        "",
        response_model=list[FullProductPublic],
        responses={
            status.HTTP_200_OK:{
                "description": "OK",
                "content": {
                    "application/json": {
                        "example":[
                            {
                                "product_id": 6,
                                "sku": "SH0002",
                                "product_name": "Basic shirt",
                                "brand": "Lacoste",
                                "product_category": "Shirts",
                                "available": True,
                                "product_variants": [
                                    {
                                        "variant_id": 13,
                                        "product_id": 6,
                                        "size": "L",
                                        "color": "Black",
                                        "stock": 5,
                                        "price": 45000.0
                                    }
                                ]
                            },
                            {
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
                        ]
                    }
                }
            }
        }
)
async def get_products(
    session: SessionDep,
    limit:  int = 10,
    offset: int = 0,
    brand: str | None = None,
    category: Annotated[str | None, Query()] = None,
    size: Annotated[str | None, Query()] = None,
    color: Annotated[str | None, Query()] = None,
    min_price: Annotated[float | None, Query()] = None,
    max_price: Annotated[float | None, Query()] = None,
):
    
    """
    Retrieves a list of products along with their full details. The results can be filtered by passing
    any of the following optional parameters:

    - **limit (int)**: Maximum number of products to return.
    - **offset (int)**: Number of products to skip before starting to return results.
    - **brand (str)**: The product's brand.
    - **category (str)**: Product category name (e.g., "T-SHIRTS").
    - **size (str)**: Product size (e.g., "XL").
    - **color (str)**: Product color (e.g., "Red").
    - **min_price (float)**: Minimum price to include in the results.
    - **max_price (float)**: Maximum price to include in the results.
    """

    # Get the list of products
    products = ProductCrud.get_products(
        session=session,
        limit=limit,
        offset=offset,
        brand=brand,
        category=category,
        size=size,
        color=color,
        min_price=min_price,
        max_price=max_price
    )

    # Return the list of products
    return products
###################################################################################################

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
        status.HTTP_404_NOT_FOUND: example_sku_notfound
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

###################################################################################################

###################################################################################################
# UPDATE ENDPOINTS

###################################################################################################
# Update a base product
@router.patch(
    "/{sku}",
    response_model=ProductBasePublic,
    dependencies=[Depends(required_role("admin"))],
    responses={
        status.HTTP_200_OK:{
            "description": "OK",
            "content": {
                "application/json":{
                    "example": {    
                        "product_id": 16,
                        "sku": "SH0012",
                        "product_name": "Athletic Tee",
                        "brand": "Under Armour",
                        "product_category_id": 1,
                        "available": True
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: example_sku_notfound
    }
)
async def update_base_product(
    session: SessionDep, 
    sku: str, 
    product_update: Annotated[ProductUpdate, Body(example={"product_name": "Athletic Tee"})]
) -> ProductBasePublic:
    
    """
    Updates a base product by passing its sku and the fields to be updated, like product name, 
    brand, category or availability.

    - **sku (str)**: The product's sku.
    - **product_update (ProductUpdate)**: Data to modify the product.
    """
    
    # Exclude unset fields
    product_data = product_update.model_dump(exclude_unset=True)

    # Update the product
    updated_product = ProductCrud.update_base_product(session, sku, product_update=product_data)

    # Return the updated product
    return updated_product
###################################################################################################

###################################################################################################
# Update a product variant
@router.patch(
    "/variants/{variant_id}",
    response_model=ProductVariantPublic,
    dependencies=[Depends(required_role("admin"))],
    responses={
        status.HTTP_200_OK:{
            "description": "OK",
            "content": {
                "application/json":{
                    "example": {
                        "variant_id": 20,
                        "product_id": 18,
                        "size": "XXL",
                        "color": "Lightblue",
                        "stock": 22,
                        "price": 86000.0
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: example_variant_notfound
    }
)
async def update_product_variant(
    session: SessionDep,
    variant_id: int,
    variant_update: Annotated[
        ProductVariantUpdate, 
        Body(example={"stock": 10, "price": 86000.00})
    ]
) -> ProductVariantPublic:
    
    """
    Updates a product variant by passing its id and the data to modify the product, like price or stock.

    - **variant_id (int)**: The product variant's id.
    - **variant_update (ProductVariantUpdate)**: Data to update the product variant.
    """
    
    # Get the data to update the product excluding unset fields
    variant_data = variant_update.model_dump(exclude_unset=True)

    # Update the product variant
    updated_product_variant = ProductCrud.update_product_variant(
        session=session, variant_id=variant_id, variant_update=variant_data
    )

    # Return the updated product variant
    return updated_product_variant
###################################################################################################

###################################################################################################
# Update a product variant availability
@router.patch(
    "/{sku}/status",
    response_model=ProductBasePublic,
    dependencies=[Depends(required_role("admin"))],
    responses={
        status.HTTP_200_OK:{
            "description": "OK",
            "content": {
                "application/json":{
                    "example":{
                        "product_id": 18,
                        "sku": "SH0014",
                        "product_name": "Eco Cotton T-Shirt",
                        "brand": "Patagonia",
                        "product_category_id": 1,
                        "available": False
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: example_variant_notfound
    }
)
async def change_product_availability(
    session: SessionDep,
    sku: str,
    available: Annotated[bool, Query()]
) -> ProductBasePublic:
    
    # Deactivate product if availability=False
    if available is False:
        product_variant = ProductCrud.deactivate_product(session, sku)

    if available is True:
        product_variant = ProductCrud.reactivate_product(session, sku)
    
    # Return the product
    return product_variant
###################################################################################################

###################################################################################################


###################################################################################################
# DELETE ENDPOINTS

###################################################################################################
# Delete a base product
@router.delete(
    "/{sku}",
    response_model=ProductBasePublic,
    dependencies=[Depends(required_role("admin"))],
    responses={
        status.HTTP_200_OK: {
            "description": "OK",
            "content": {
                "application/json": {
                    "example": {
                        "product_id": 23,
                        "sku": "SH0019",
                        "product_name": "Colorblock T-Shirt",
                        "brand": "Puma",
                        "product_category_id": 1,
                        "available": True
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: example_sku_notfound
    }
)
async def delete_base_product(session: SessionDep, sku: str) -> ProductBasePublic:
    
    """
    Deletes a base product by passing its sku.

    - **sku (str)**: The base product's sku.
    """

    # Delete the product
    deleted_product = ProductCrud.delete_base_product(session, sku)

    # Return the deleted product
    return deleted_product
###################################################################################################

###################################################################################################
# Delete a product variant
@router.delete(
    "/variants/{variant_id}",
    response_model=ProductVariantPublic,
    dependencies=[Depends(required_role("admin"))],
    responses={
        status.HTTP_200_OK: {
            "description": "OK",
            "content":{
                "application/json":{
                    "example":{
                        "variant_id": 12,
                        "product_id": 5,
                        "size": "XL",
                        "color": "White",
                        "stock": 2,
                        "price": 89000.0
                    }
                }
            }
        },
        status.HTTP_404_NOT_FOUND: example_variant_notfound
    }
)
async def delete_product_variant(session: SessionDep, variant_id: int) -> ProductVariantPublic:

    """
    Deletes a product variant info by passing the variant_id.

    - **variant_id (int)**: The product variant's id.
    """
    
    # Delete the product variant
    deleted_variant = ProductCrud.delete_product_variant(session, variant_id)

    # Return the deleted product variant
    return deleted_variant
###################################################################################################

###################################################################################################