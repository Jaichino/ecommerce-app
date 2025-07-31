##################################
# API Router for Products module #
##################################


###################################################################################################
# Imports

from typing import Annotated
from sqlmodel import Session
from fastapi import APIRouter, Depends, status

from app.db.database import get_session



from app.schemas.products import ProductBaseCreate, ProductBasePublic

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

# Create new base products
@router.post(
        "",
        response_model=ProductBasePublic
)
async def create_base_product(
    session: SessionDep,
    product: ProductBaseCreate
) -> ProductBasePublic:
    
    """
    Creates a new base product by passing a JSON object with fields like sku, product name and
    category.
    """

    # Creates the product
    created_product = ProductCrud.create_product_base(session=session, product_in=product)

    # Return the product
    return created_product

###################################################################################################
