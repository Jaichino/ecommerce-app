################################
#       CRUD for Orders       #
################################


###################################################################################################
# Imports

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.schemas.orders import (
    FullOrderPublic, OrderDetailCreate, OrderUpdate, OrderInfo, OrderCreate, OrderStatus, 
    OrderDetailPublic, ShippingStatus
)
from app.schemas.users import FullUserPublic

from app.models.orders import Order, OrderStatus, PaymentMethod
from app.models.order_detail import OrderDetail

from app.crud.products import ProductCrud
from app.crud.users import UsersCrud
from app.crud.shippers import ShippersCrud

from app.exceptions import (
    ProductVariantNotFoundError, OrderNotFoundError, InvalidShipperTokenError
)

from app.utils.shipper_token_generator import shipper_token_generator, verify_shipper_token

###################################################################################################


###################################################################################################
# CRUD

class OrdersCrud():

    ###############################################################################################
    # Create

    @staticmethod
    def create_order_detail(
        session: Session,
        order_id: int,
        details: list[OrderDetailCreate]
    ) -> list[OrderDetailPublic]:
        
        """      
        Creates an order detail, passing a list of products with the quantities to be sold. 
        Deducts the quantity sold from the corresponding product.

        Args:
            session (Session): The SQLModel session to interact with the database.
            order_id (int): The number of the current order.
            details (list[OrderDetailCreate]): A list with the products and quantities to be sold.
        
        Returns:
            list[OrderDetailPublic]: A list of the order details. 
        """
        
        details_public = []

        # Create a OrderDetail for each detail
        for detail in details:

            # Get the variant info
            variant = ProductCrud.get_variant_info(
                session, variant_id=detail.product_variant_id
            )

            if not variant:
                raise ProductVariantNotFoundError(variant_id=detail.product_variant_id)
            
            # Get the price
            price = variant.price

            # Create a OrderDetail
            order_detail = OrderDetail(
                order_id=order_id,
                product_id=detail.product_variant_id,
                quantity=detail.quantity,
                price=price
            )

            # Discount the quantity sold of the product
            ProductCrud.substract_product(
                session, variant_id=detail.product_variant_id, quantity_substracted=detail.quantity
            )

            # Create the OrderDetailPublic
            sku = variant.prod.sku # prod is a Relationship with Products model
            product_name = variant.prod.product_name
            detail_public = OrderDetailPublic(
                sku=sku,
                product_name=product_name,
                size=variant.size,
                color=variant.color,
                quantity=detail.quantity,
                price=price
            )

            # Add the OrderDetail to the session
            session.add(order_detail)

            # Add OrderDetailPublic to the list
            details_public.append(detail_public)

        # Return the list of OrderDetailPublic
        return details_public



    @staticmethod
    def create_order(
        session:Session,
        client_id: int,
        order_create: OrderCreate,
        SHIPPER_TOKEN_BASE: int
    ) -> OrderInfo:
        
        """
        Creates a new order. The method assings a shipper token if the amount of the order is greater
        than a limit specified by SHIPPER_TOKEN_BASE.
        The method also create the respective order details and discount the products from the stock.

        Args:
            session (Session): The SQLModel session to interact with the database.
            client_id (int): The id of the client who make the order.
            order_create (OrderCreate): Data for the creation of the order.
            SHIPPER_TOKEN_BASE (int): The minimum order's amount to get a shipper token.
        
        Returns:
            OrderInfo: Information of the created order.
        """
        
        try:
            # Calculate the total of the order
            total_order = 0
            for item in order_create.order_items:

                # Get the variant
                variant_info = ProductCrud.get_variant_info(session, item.product_variant_id)

                # Get the price
                unit_price = variant_info.price

                # Subtotal (quantity * price)
                item_subtotal = item.quantity * unit_price
                
                # total_order + subtotal
                total_order += item_subtotal

            # Generate the shipper token
            shipper_token = shipper_token_generator() if SHIPPER_TOKEN_BASE < total_order else None

            # Create the order
            order = Order(
                client_id=client_id,
                shipper_id=order_create.shipper_id,
                order_status=order_create.order_status,
                payment_method=order_create.payment_method,
                total_order=total_order,
                shipper_token=shipper_token
            )

            session.add(order)
            session.flush() # Generates the order but not permanently in db
            session.refresh(order)

            # Create the OrderDetails
            order_details = OrdersCrud.create_order_detail(
                session, order_id=order.order_id, details=order_create.order_items
            )

            # Commit session
            session.commit()

            # Create and return the OrderInfo
            order_info = OrderInfo(
                order_id=order.order_id,
                created_at=order.created_at,
                order_status=order.order_status,
                payment_method=order.payment_method,
                total_order=order.total_order,
                shipper_id=order.shipper_id,
                order_details=order_details,
                shipper_token=order.shipper_token
            )

            return order_info

        except Exception as e:
            session.rollback()
            raise e

    ###############################################################################################


    ###############################################################################################
    # Read

    @staticmethod
    def get_order_info(session: Session, order_id: int) -> OrderInfo:

        """
        Gets a order information by passing its order_id.

        Args:
            session (Session): The SQLModel session to interact with the database.
            order_id (int): The order's id.
        
        Returns:
            OrderInfo: Information about the order.
        """

        # Get the order
        order = session.exec(
            select(Order)
            .options(selectinload(Order.details))
            .where(Order.order_id == order_id)
        ).first()

        # Raise exception if there's no order
        if not order:
            raise OrderNotFoundError(order_id=order_id)

        # Create the list of details
        details_public = []

        for detail in order.details:

            # Get info of the product in that detail
            product_info = ProductCrud.get_variant_info(session, detail.product_id)
            if not product_info:
                raise ProductVariantNotFoundError(variant_id=detail.product_id)

            detail_public = OrderDetailPublic(
                sku=product_info.prod.sku,
                product_name=product_info.prod.product_name,
                size=product_info.size,
                color=product_info.color,
                quantity=detail.quantity,
                price=detail.price
            )

            details_public.append(detail_public)

        # Create and return the order info (OrderInfo)
        order_info = OrderInfo(
            order_id=order.order_id,
            created_at=order.created_at,
            order_status=order.order_status,
            payment_method=order.payment_method,
            total_order=order.total_order,
            shipper_id=order.shipper_id,
            shipper_token=order.shipper_token,
            order_details=details_public
        )

        return order_info


    @staticmethod
    def get_fullorder_info(session: Session, order_id: int) -> FullOrderPublic:
        
        """
        Gets a detailed order information, like full information of the user, shipper and products.

        Args:
            session (Session): The SQLModel session to interact with the database.
            order_id (int): The order's id.
        
        Returns:
            FullOrderPublic: Full information about the order.
        """
        # Get the order to consult
        order = session.exec(
            select(Order)
            .options(
                selectinload(Order.client), 
                selectinload(Order.details), 
                selectinload(Order.shipper)
            )
            .where(Order.order_id == order_id)
        ).first()

        # Raise exception if there's no order
        if not order:
            raise OrderNotFoundError(order_id=order_id)

        # Create the user info (FullUserPublic)
        user = order.client
        user_info = UsersCrud.get_user_by_dni(session, user.user_dni)

        # Create the shipper info (ShipperPublic)
        shipper = order.shipper
        shipper_info = ShippersCrud.get_shipper_by_id(session, shipper_id=shipper.shipper_id)

        # Create the order info (OrderInfo)
        order_info = OrdersCrud.get_order_info(session, order_id=order_id)

        # Return the FullOrderPublic
        return FullOrderPublic(
            user=user_info,
            shipper=shipper_info,
            order_info=order_info
        )
    

    @staticmethod
    def get_shipper_token(session: Session, order_id: int) -> int | None:
        
        """
        Gets the stored shipped token from a specific order.

        Args:
            session (Session): The SQLModel session to interact with the database.
            order_id (int): The order's id.
        
        Returns:
            The shipper token. None if there's no shipper token associated to the order.
        """

        # Gets the order
        order = session.get(Order, order_id)

        # Raise exception if there's no order
        if not order:
            raise OrderNotFoundError(order_id=order_id)
        
        # Get the shipper token from order
        shipper_token = order.shipper_token

        # Return the token
        return shipper_token

    ###############################################################################################


    ###############################################################################################
    # Update

    @staticmethod
    def confirm_order(session: Session, order_id: int) -> ShippingStatus:
        """
        Updates the status of the order to 'confirmed' when the store confirms the order.

        Args:
            session (Session): The SQLModel session to interact with the database.
            order_id (int): The order's id.

        Returns:
            DeliveryStatus: The updated status of the order.
        """

        # Gets the order to update
        order_to_update = session.get(Order, order_id)

        # Raise exception if there's no order
        if not order_to_update:
            raise OrderNotFoundError(order_id=order_id)

        # Updates the order_status to confirmed
        order_to_update.order_status = OrderStatus.confirmed
        session.add(order_to_update)
        session.commit()
        session.refresh(order_to_update)

        # Return a DeliveryStatus object
        return ShippingStatus.model_validate(order_to_update)
    

    @staticmethod
    def start_shipping(session: Session, order_id: int) -> ShippingStatus:
        """
        Updates the status of the order to 'shipped' when the shipper starts the delivery.

        Args:
            session (Session): The SQLModel session to interact with the database.
            order_id (int): The order's id.

        Returns:
            DeliveryStatus: The updated status of the order.
        """

        # Gets the order to update
        order_to_update = session.get(Order, order_id)

        # Raise exception if there's no order
        if not order_to_update:
            raise OrderNotFoundError(order_id=order_id)

        # Updates the order_status to shipped
        order_to_update.order_status = OrderStatus.shipped
        session.add(order_to_update)
        session.commit()
        session.refresh(order_to_update)

        # Return a DeliveryStatus object
        return ShippingStatus.model_validate(order_to_update)


    @staticmethod
    def finish_shipping(session: Session, order_id: int, token: int | None = None) -> ShippingStatus:
        
        """
        Updates the status of the order to 'delivered' when the client receives the products. If
        the order has a token, the client must pass this token to the shipper and verify it.

        Args:
            session (Session): The SQLModel session to interact with the database.
            order_id (int): The order's id.
            token (int): The shipper token given to the client.
        
        Returns:
            DeliveryStatus: The updated status of the order.
        """
        
        # Gets the order to update
        order_to_update = session.get(Order, order_id)

        # Raise exception if there's no order
        if not order_to_update:
            raise OrderNotFoundError(order_id=order_id)
        
        # Verify if the order has a shipper token
        shipper_token = OrdersCrud.get_shipper_token(session, order_id)

        # If there's a shipper token, verify with the given for the client
        if shipper_token:
            verify = verify_shipper_token(token, shipper_token)
            # Raise exception if the token is invalid
            if not verify:
                raise InvalidShipperTokenError(token=token)
        
        # Update the order_status to delivered
        order_to_update.order_status = OrderStatus.delivered
        session.add(order_to_update)
        session.commit()
        session.refresh(order_to_update)

        # Return a DeliveryStatus object
        return ShippingStatus.model_validate(order_to_update)
    

    @staticmethod
    def cancel_order(session: Session, order_id: int) -> ShippingStatus:
        """
        Updates the status of the order to 'canceled' when the client cancels the order.

        Args:
            session (Session): The SQLModel session to interact with the database.
            order_id (int): The order's id.

        Returns:
            DeliveryStatus: The updated status of the order.
        """

        # Gets the order to update
        order_to_update = session.get(Order, order_id)

        # Raise exception if there's no order
        if not order_to_update:
            raise OrderNotFoundError(order_id=order_id)

        # Updates the order_status to canceled
        order_to_update.order_status = OrderStatus.canceled
        session.add(order_to_update)
        session.commit()
        session.refresh(order_to_update)

        # Return a DeliveryStatus object
        return ShippingStatus.model_validate(order_to_update)

    ###############################################################################################


    ###############################################################################################
    # Delete

    @staticmethod
    def delete_order(session: Session, order_id: int) -> OrderInfo:
        
        """
        Deletes a order definitely from database.

        Args:
            session (Session): The SQLModel session to interact with the database.
            order_id (int): The order's id.
        
        Returns:
            OrderInfo: Information of the deleted order.
        """

        # Gets the order
        order_to_delete = session.get(Order, order_id)

        # Raise exception if there's no order
        if not order_to_delete:
            raise OrderNotFoundError(order_id=order_id)
        
        # Get order information
        order_info = OrdersCrud.get_order_info(session, order_id)

        # Delete the order
        session.delete(order_to_delete)
        session.commit()

        # Return the order information
        return order_info

    ###############################################################################################

###################################################################################################
