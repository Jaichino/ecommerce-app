################################
#      CRUD for Products       #
################################


###################################################################################################
# Imports

from sqlmodel import Session, select, between, join
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from app.models.products import Products, ProductCategory, ProductVariant
from app.schemas.products import (
    ProductBaseCreate, ProductVariantCreate, CategoryCreate, ProductBasePublic, CategoryPublic,
    ProductVariantPublic, ProductUpdate, FullProductPublic, ProductVariantUpdate, CategoryUpdate
)
from app.exceptions import (
    CategoryNotFoundError, ProductNotFoundError, ProductVariantNotFoundError, 
    InsufficientStockError
)

###################################################################################################



###################################################################################################
# CRUD

class ProductCrud():

    ###############################################################################################
    # Create

    @staticmethod
    def create_product_base(session: Session, product_in: ProductBaseCreate) -> Products:

        """
        Creates a new base product. If a product with the passed SKU already exists and it's not
        available then reactivates it by setting 'available=True'. If it's already available, then
        return it.
        
        Args:
            session (Session): The SQLModel session to interact with the database.
            product_in (ProductBaseCreate): Data for the product to be created.

        Returns:
            A Products object.
        """

        # Validate the ProductBaseCreate as Products
        product_db = Products.model_validate(product_in)

        # Verify if the product_category_id exists
        category = session.get(ProductCategory, product_db.product_category_id)
        if not category:
            raise CategoryNotFoundError(category_id=product_db.product_category_id)


        try:
            # Verify if the product already exists in database
            product_exists = ProductCrud.get_base_product_by_sku(session, product_db.sku)
        except ProductNotFoundError:
            product_exists = None

        # If the product exists and is not available, then reactive it.
        if product_exists and product_exists.available is False:
            ProductCrud.reactivate_product(session, product_exists.sku)
        
        # If the product exists and is available, then return it.
        if product_exists and product_exists.available is True:
            return product_exists

        if not product_exists:
            # Add product_db to the session and commit, then return the created product
            session.add(product_db)
            session.commit()
            session.refresh(product_db)

            return product_db


    @staticmethod
    def create_product_category(session: Session, category: CategoryCreate) -> ProductCategory:
        
        """
        Creates a new product category by passing the name of the category.

        Args:
            session (Session): The SQLModel session to interact with the database.
            category (CategoryCreate): Data of the category.

        Returns:
            CategoryPublic: The created category.
        """

        # Uppercase the category_name
        category.category = category.category.upper()
        
        # Validate the CategoryCreate as a ProductCategory
        category_db = ProductCategory.model_validate(category)

        # Add category_db to the session and commit, then return the created category
        session.add(category_db)
        session.commit()
        session.refresh(category_db)

        return category_db


    @staticmethod
    def create_product_variant(
        session: Session, sku: str, product_variant: ProductVariantCreate
    ) -> ProductVariant:
        
        """
        Creates a new product variant associated with a base product identified by its SKU. 
        If a variant with the same product_id, size, and color already exists (enforced by 
        a UNIQUE constraint), its stock and price will be updated instead of creating a new 
        record. 
        
        Args:
            session (Session): The SQLModel session to interact with the database.
            sku (str): The SKU of the base product.
            product_variant (ProductVariantCreate): Data for the variant to be created.

        Returns:
            ProductVariant: The created or updated variant.
        """
        
        # Get the product with the sku
        product = ProductCrud.get_base_product_by_sku(session, sku)

        # Validate the ProductVariantCreate as a ProductVariant, adding product_id
        variant_db = ProductVariant(**product_variant.model_dump(), product_id=product.product_id)

        try:
            # Add variant_db to the session and commit, then return the created variant
            session.add(variant_db)
            session.commit()
            session.refresh(variant_db)

            return variant_db

        except IntegrityError:

            session.rollback()

            # If the variant exists, then add quantity and update the price to the existing variant
            existent_variant = session.exec(
                select(ProductVariant)
                .where(
                    ProductVariant.product_id == variant_db.product_id,
                    ProductVariant.size == variant_db.size,
                    ProductVariant.color == variant_db.color
                )
            ).one()

            # Add the quantity and actualice the price to the existing product
            existent_variant.stock += variant_db.stock
            existent_variant.price = variant_db.price

            session.add(existent_variant)
            session.commit()
            session.refresh(existent_variant)

            return existent_variant

    ###############################################################################################


    ###############################################################################################
    # Read

    @staticmethod
    def get_base_product_by_sku(
        session: Session,
        sku: str
    ) -> Products | None:
        
        """
        Gets a ProductBasePublic available or not by passing the product's sku.

        Args:
            session (Session): The SQLModel session to interact with the database.
            sku (str): The SKU of the base product.

        Returns:
            A Products object or None if the sku couldn't match any product.
        """
        
        # Get the product with the sku
        product = session.exec(
            select(Products).where(Products.sku == sku)
        ).first()

        # Raise exception if the sku couldn't find any product
        if not product:
            raise ProductNotFoundError(sku=sku)
        
        # Return the product
        return product


    @staticmethod
    def get_full_product_by_sku(
        session: Session,
        sku: str
    ) -> FullProductPublic:
        
        """
        Gets a FullProductPublic available or not by passing the product's sku.

        Args:
            session (Session): The SQLModel session to interact with the database.
            sku (str): The SKU of the base product.

        Returns:
            A FullProductPublic. None if the sku couldn't match any product.
        """
        
        # Get the product with the sku
        product = session.exec(
            select(Products)
            .where(Products.sku == sku)
            .options(selectinload(Products.variants), selectinload(Products.category))
        ).first()

        # Raise exception if the sku doesn't match with any products
        if not product:
            raise ProductNotFoundError(sku=sku)

        # Get the product's variants (list[ProductVariant])
        variants = product.variants

        # Get the product_category name
        category = product.category.category

        # Get the FullProductPublic and return it
        product_public = FullProductPublic(
            product_id=product.product_id,
            sku=product.sku,
            product_name=product.product_name,
            brand=product.brand,
            product_category=category,
            available=product.available,
            product_variants=[
                ProductVariantPublic(**variant.model_dump()) for variant in variants
            ]
        )

        return product_public


    @staticmethod
    def get_products(
        session: Session,
        available: bool = True,
        brand: str | None = None,
        category: str | None = None,
        size: str | None = None,
        color: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 10,
        offset: int = 0
    ) -> list[FullProductPublic]:
        
        """
        Gets all the products, filtering by optional parameters like brand, category, size, color and
        prices.

        Args:
            session (Session): The SQLModel session to interact with the database.
            available (bool): True if the product is available, False if not.
            brand (str): The product's brand.
            category (str): The product's category.
            size (str): The product's size.
            color (str): The product's color.
            min_price (float): Minimun price to filter.
            max_price (float): Maximum price to filter.
            limit (int): Maximun number of products returned.
            offset (int): Number of products to skip before starting to return results.
        
        Returns:
            a list of FullProductPublic
        """

        # Initial query
        query = (
            select(Products)
            .options(selectinload(Products.variants), selectinload(Products.category))
            .where(Products.available == available)
        )

        # Filter for brand
        if brand:
            query = (
                query
                .where(Products.brand == brand)
            )

        # Filter for category if category is not None
        if category:
            query = (
                query
                .where(Products.category.has(category=category))
            )


        # Size, color and price filters, need a join
        if size or color or (min_price is not None and max_price is not None):
            query = query.join(ProductVariant)

        # If size is not None, then filter by size too
        if size:
            query = (
                query
                .where(ProductVariant.size == size)
            )

        # If color is not None, then filter by color too
        if color:
            query = (
                query
                .where(ProductVariant.color == color)
            )

        # If min and max price, the filter between the 2 prices
        if min_price is not None and max_price is not None:
            query = (
                query
                .where(
                    between(ProductVariant.price, min_price, max_price)
                )
            )
        
        # Order the results by name and add offset and limit for pagination
        query = query.order_by(Products.product_name).offset(offset).limit(limit)

        # Get the resultant list of Products
        products = session.exec(query).unique().all()

        # Get the list of FullProductPublic and return it
        public_products = []

        for product in products:

            variants = product.variants

            base_product = FullProductPublic(
                product_id=product.product_id,
                sku=product.sku,
                product_name=product.product_name,
                brand=product.brand,
                product_category=product.category.category,
                available=product.available,
                product_variants=[
                    ProductVariantPublic(**variant.model_dump()) for variant in variants
                ]
            )

            public_products.append(base_product)
        
        return public_products


    @staticmethod
    def get_variant_info(session: Session, variant_id: int) -> ProductVariant:

        """
        Gets a product variant info.

        Args:
            session (Session): The SQLModel session to interact with the database.
            variant_id (int): The product variant's id
        
        Returns:
            ProductVariant: The product variant's information.
        """

        # Get the variant
        variant = session.exec(
            select(ProductVariant)
            .options(selectinload(ProductVariant.prod))
            .where(ProductVariant.variant_id == variant_id)
        ).first()

        # Raise exception if variant_id couldn't get any variant
        if not variant:
            raise ProductVariantNotFoundError(variant_id=variant_id)

        # Return the ProductVariant
        return variant


    @staticmethod
    def get_categories(session: Session) -> list[ProductCategory] | None:

        """
        Gets all the existing product categories. If there is no category, return None.
        """

        # Get all the categories ordered by name
        categories = session.exec(
            select(ProductCategory).order_by(ProductCategory.category)
        ).all()

        # Return None if there is no category
        if not categories:
            return None

        # Return the categories
        return categories

    ###############################################################################################


    ###############################################################################################
    # Update

    @staticmethod
    def update_base_product(
        session: Session, sku: str, product_update: ProductUpdate
    ) -> Products:
        
        """
        Updates an existing base product by passing its sku and an object ProductUpdate with the
        fields to be modified.

        Args:
            session (Session): The SQLModel session to interact with the database.
            sku (str): The product's sku.
            product_update (ProductUpdate): Data of the product to be updated.
        
        Returns:
            A Products object.
        """
        
        # Get the product to update
        product_to_update = ProductCrud.get_base_product_by_sku(session, sku)
        
        # Update the product
        product_to_update.sqlmodel_update(product_update)
        session.add(product_to_update)
        session.commit()
        session.refresh(product_to_update)

        # Return the updated product
        return product_to_update


    @staticmethod
    def update_category(
        session: Session, 
        category_id: int,
        category_update: CategoryUpdate
    ) -> CategoryPublic:
        
        """
        Updates an existing product category by passing its category_id and an object 
        CategoryUpdate with the fields to be modified.

        Args:
            session (Session): The SQLModel session to interact with the database.
            category_id (int): The category's id.
            category_update (CategoryUpdate): Data of the category to be updated.
        
        Returns:
            A ProductCategory object.
        """

        # Get the category to update
        category_to_update = session.exec(
            select(ProductCategory).where(ProductCategory.category_id == category_id)
        ).first()

        # Raise exception if couldn't get the category
        if not category_to_update:
            raise CategoryNotFoundError(category_id=category_id)
        
        # Update the category
        category_to_update.sqlmodel_update(category_update)
        session.add(category_to_update)
        session.commit()
        session.refresh(category_to_update)

        # Return a CategoryPublic
        return CategoryPublic.model_validate(category_to_update)


    @staticmethod
    def update_product_variant(
        session: Session, variant_id: int, variant_update: ProductVariantUpdate
    ) -> ProductVariant:
        
        """
        Updates an existing product variant by passing its variant_id and an object ProductVariantUpdate
        with the fields to be modified.

        Args:
            session (Session): The SQLModel session to interact with the database.
            variant_id (int): The ID of the product variant.
            variant_update (ProductVariantUpdate): Data of the product variant to be updated.
        
        Returns:
            A ProductVariant object.
        """

        # Get the variant to update
        variant_to_update = ProductCrud.get_variant_info(session, variant_id)
        
        # Update the product and return it
        variant_to_update.sqlmodel_update(variant_update)
        session.add(variant_to_update)
        session.commit()
        session.refresh(variant_to_update)

        return variant_to_update


    @staticmethod
    def deactivate_product(session: Session, sku: str) -> Products:
        
        """
        Deactivates a base product turning the available field to False.

        Args:
            session (Session): The SQLModel session to interact with the database.
            sku (str): The product's sku.
        
        Returns:
            A Products object.
        """

        # Get the product
        product = ProductCrud.get_base_product_by_sku(session, sku)
        
        # Deactivate the product turning available field to False
        product.available = False

        # Commit changes
        session.add(product)
        session.commit()
        session.refresh(product)

        return product
    

    @staticmethod
    def reactivate_product(session: Session, sku: str) -> Products:
        
        """
        Reactivates a base product turning the available field to True.

        Args:
            session (Session): The SQLModel session to interact with the database.
            sku (str): The product's sku.
        
        Returns:
            A Products.
        """

        # Get the product
        product = session.exec(
            select(Products).where(Products.sku == sku)
        ).first()

        # Raise exception if the sku couldn't match any product
        if not product:
            raise ProductNotFoundError(sku=sku)
        
        # Reactivate the product turning available field to True
        product.available = True

        # Commit changes
        session.add(product)
        session.commit()
        session.refresh(product)

        # Return the product
        return product


    @staticmethod
    def substract_product(session: Session, variant_id: int, quantity_substracted: int):

        """
        Discount the quantity sold of a product.

        Args:
            session (Session): The SQLModel session to interact with the database.
            variant_id (int): The variant's id.
            quantity_substracted (int): The quantity sold of the product.
        """

        # Get the variant
        variant = ProductCrud.get_variant_info(session, variant_id)
        
        # Raise exception if stock < quantity_substracted
        if variant.stock < quantity_substracted:
            raise InsufficientStockError(variant_id=variant_id)

        # Update the variant stock
        variant.stock -= quantity_substracted
        session.add(variant)

    ###############################################################################################


    ###############################################################################################
    # Delete

    @staticmethod
    def delete_base_product(session: Session, sku: str) -> Products:
        
        """
        Deletes a base product by passing its sku.

        Args:
            session (Session): The SQLModel session to interact with the database.
            sku (str): The product's sku.
        
        Returns:
            A Products object.
        """

        # Get the product to delete
        product_to_delete = ProductCrud.get_base_product_by_sku(session, sku)

        # Delete the product
        session.delete(product_to_delete)
        session.commit()

        # Return the deleted product
        return product_to_delete
    
    
    @staticmethod
    def delete_category(session: Session, category_id: int) -> ProductCategory:

        """
        Deletes a product category by passing its category_id.

        Args:
            session (Session): The SQLModel session to interact with the database.
            category_id (int): The category's id.
        
        Returns:
            A ProductCategory object.
        """

        # Get the category to delete
        category_to_delete = session.exec(
            select(ProductCategory).where(ProductCategory.category_id == category_id) 
        ).first()

        # Raise exception if category_id couldn't match any category
        if not category_to_delete:
            raise CategoryNotFoundError(category_id=category_id)
        
        # Delete the category
        session.delete(category_to_delete)
        session.commit()

        # Return the deleted category
        return category_to_delete


    @staticmethod
    def delete_product_variant(session: Session, variant_id: int) -> ProductVariant:
        
        """
        Deletes a product variant by passing its variant_id.

        Args:
            session (Session): The SQLModel session to interact with the database.
            variant_id (int): The variant's id.
        
        Returns:
            A ProductVariant object.
        """

        # Get the variant to delete
        variant_to_delete = ProductCrud.get_variant_info(session, variant_id)
        
        # Delete and return the variant
        session.delete(variant_to_delete)
        session.commit()

        return variant_to_delete

    ###############################################################################################

###################################################################################################