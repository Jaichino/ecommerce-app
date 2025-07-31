#####################
# Custom exceptions #
#####################


###################################################################################################
#                                     PRODUCTS EXCEPTIONS                                         # 
###################################################################################################

class CategoryNotFoundError(Exception):
    def __init__(self, category_id: int):
        self.category_id = category_id
        self.mensaje = f"Category with category_id '{self.category_id}' not found!"
        super().__init__(self.mensaje)


class ProductNotFoundError(Exception):
    def __init__(self, sku: str):
        self.sku = sku
        self.mensaje = f"Product with sku '{self.sku}' not found!"
        super().__init__(self.mensaje)


class ProductVariantNotFoundError(Exception):
    def __init__(self, variant_id: int):
        self.variant_id = variant_id
        self.mensaje = f"Variant with variant_id '{self.variant_id}' not found!"
        super().__init__(self.mensaje)


class InsufficientStockError(Exception):
    def __init__(self, variant_id: int):
        self.variant_id = variant_id
        self.mensaje = f"Insufficient stock for product '{self.variant_id}'"
        super().__init__(self.mensaje)

###################################################################################################
#                                         USERS EXCEPTIONS                                        # 
###################################################################################################

class UserAlreadyExistsError(Exception):
    def __init__(self, field: str):
        self.field = field
        self.mensaje = f"User with this {self.field} already exists!"
        super().__init__(self.mensaje)


class UserNotFoundError(Exception):
    def __init__(
            self, 
            user_id: int | None = None,
            user_dni: int | None = None,
            user_email: str | None = None
    ):
        self.user_id = user_id
        self.user_dni = user_dni
        self.user_email = user_email

        if user_id:
            self.mensaje = f"User with id '{self.user_id}' not found!"
        
        if user_dni:
            self.mensaje = f"User with dni '{self.user_dni}' not found!"
        
        if user_email:
            self.mensaje = f"User with email '{self.user_email}' not found!"


        super().__init__(self.mensaje)


###################################################################################################
#                                      SHIPPERS EXCEPTIONS                                        # 
###################################################################################################

class ShipperNotFoundError(Exception):
    def __init__(self, shipper_id: int):
        self.shipper_id = shipper_id
        self.mensaje = f"Shipper with shipper_id '{self.shipper_id}' not found!"
        super().__init__(self.mensaje)


###################################################################################################
#                                       ORDERS EXCEPTIONS                                         # 
###################################################################################################

class OrderNotFoundError(Exception):
    def __init__(self, order_id: int):
        self.order_id = order_id
        self.mensaje = f"Order with id '{self.order_id}' not found!"
        super().__init__(self.mensaje)


class InvalidShipperTokenError(Exception):
    def __init__(self, token: int):
        self.token = token
        self.mensaje = f"Token '{self.token}' is invalid!"
        super().__init__(self.mensaje)

