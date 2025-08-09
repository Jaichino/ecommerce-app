########
# MAIN #
########

###################################################################################################
# Imports

from fastapi import FastAPI, Depends

from app.models import products, shippers, users, orders, order_detail

from app.db.database import create_db_and_tables

from app.exceptions import (
    CategoryNotFoundError, ProductNotFoundError, ProductVariantNotFoundError
)

from app.exception_handlers import categorynotfound_exception_handler
from app.exception_handlers import productnotfound_exception_handler
from app.exception_handlers import productvariantnotfound_exception_handler

from app.routers import login
from app.routers import products

###################################################################################################


###################################################################################################
# API Configuration

app = FastAPI()

###################################################################################################


###################################################################################################
# Exception handlers
app.add_exception_handler(CategoryNotFoundError, categorynotfound_exception_handler)
app.add_exception_handler(ProductNotFoundError, productnotfound_exception_handler)
app.add_exception_handler(ProductVariantNotFoundError, productvariantnotfound_exception_handler)

###################################################################################################


###################################################################################################
# Routers
app.include_router(products.router)
app.include_router(login.router)



###################################################################################################

###################################################################################################
# Database models initializing

@app.on_event("startup")
async def startup():
    create_db_and_tables()

###################################################################################################