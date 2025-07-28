#####################
# Custom exceptions #
#####################


###################################################################################################
#                                       PRODUCTS MODULE                                           # 
###################################################################################################

class CategoryNotFoundError(Exception):
    def __init__(self, category_id: int):
        self.category_id = category_id
        self.mensaje = f"Category with category_id = {category_id} not exists!"
        super().__init__(self.mensaje)


class ProductNotFoundError(Exception):
    def __init__(self, sku: str):
        self.sku = sku
        self.mensaje = f"Product with sku = {sku} not found!"
        super().__init__(self.mensaje)


class ProductVariantNotFoundError(Exception):
    def __init__(self, variant_id: int):
        self.variant_id = variant_id
        self.mensaje = f"Variant with variant_id = {variant_id} not found!"
        super().__init__(self.mensaje)