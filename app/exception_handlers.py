#############################
# Custom exception handlers #
#############################

###################################################################################################
# Imports

from typing import TYPE_CHECKING
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.exceptions import (
    CategoryNotFoundError, ProductNotFoundError, ProductVariantNotFoundError, 
    InsufficientStockError
)
###################################################################################################


###################################################################################################
#                                 PRODUCTS EXCEPTION HANDLERS                                     # 
###################################################################################################

async def categorynotfound_exception_handler(request: Request, exc: CategoryNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "message": "Product category not found",
            "detail": exc.mensaje}
    )
