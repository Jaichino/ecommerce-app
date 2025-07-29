################################
#      CRUD for Shippers       #
################################


###################################################################################################
# Imports

from sqlmodel import Session, select
from app.models.shippers import Shipper
from app.schemas.shippers import ShipperCreate, ShipperPublic, ShipperUpdate
from app.exceptions import ShipperNotFoundError

###################################################################################################


###################################################################################################
# CRUD

class ShippersCrud():

    ###############################################################################################
    # Create

    @staticmethod
    def create_shipper(session: Session, shipper_create: ShipperCreate) -> ShipperPublic:

        """
        Creates a new shipper by passing shipper data like name, email and phone number.

        Args:
            session (Session): The SQLModel session to interact with the database.
            shipper (ShipperCreate): Data of the shipper.

        Returns:
            ShipperPublic: A ShipperPublic object.
        """

        # Validate the ShipperCreate as a Shipper
        shipper_db = Shipper.model_validate(shipper_create)

        # Create the shipper
        session.add(shipper_db)
        session.commit()
        session.refresh(shipper_db)

        # Return a ShipperPublic
        return ShipperPublic.model_validate(shipper_db)

    ###############################################################################################


    ###############################################################################################
    # Read

    @staticmethod
    def get_shipper_by_id(session: Session, shipper_id: int) -> ShipperPublic:

        """
        Gets a shipper by passing their id.

        Args:
            session (Session): The SQLModel session to interact with the database.
            shipper_id (int): The shipper's id.

        Returns:
            ShipperPublic: A ShipperPublic object.
        """

        # Get the shipper
        shipper = session.get(Shipper, shipper_id)

        # Raise exception if shipper_id couldn't find a shipper
        if not shipper:
            raise ShipperNotFoundError(shipper_id=shipper_id)

        # Return the ShipperPublic
        return ShipperPublic.model_validate(shipper)


    @staticmethod
    def get_shippers(session: Session) -> list[ShipperPublic] | None:

        """
        Gets the full list of shippers.

        Args:
            session (Session): The SQLModel session to interact with the database.

        Returns:
            list[ShipperPublic]: A list of ShipperPublic objects or None if there is no shipper.
        """

        # Get the shippers
        shippers = session.exec(select(Shipper).order_by(Shipper.shipper_name)).all()

        # Return None if there's no shipper
        if not shippers:
            return None

        # Return the shippers public
        shippers_public = [ShipperPublic.model_validate(shipper) for shipper in shippers]

        return shippers_public

    ###############################################################################################


    ###############################################################################################
    # Update

    @staticmethod
    def update_shipper(
        session: Session, shipper_id: int, shipper_update: ShipperUpdate
    ) -> ShipperPublic:
        
        """
        Updates a shipper passing their id and the fields to be modified, like their name, email
        and phone number.

        Args:
            session (Session): The SQLModel session to interact with the database.
            shipper_id (int): The shipper's id.
            shipper_update (ShipperUpdate): Data of the shipper to be modified.

        Returns:
            ShipperPublic: A ShipperPublic object.
        """

        # Get the shipper to be updated
        shipper_to_update = session.get(Shipper, shipper_id)

        # Raise exception if shipper_id couldn't get a shipper
        if not shipper_to_update:
            raise ShipperNotFoundError(shipper_id=shipper_id)
        
        # Update the shipper
        shipper_to_update.sqlmodel_update(shipper_update)
        session.add(shipper_to_update)
        session.commit()
        session.refresh(shipper_to_update)

        # Return the ShipperPublic
        return ShipperPublic.model_validate(shipper_to_update)

    ###############################################################################################


    ###############################################################################################
    # Delete

    @staticmethod
    def delete_shipper(session: Session, shipper_id: int) -> ShipperPublic:
        """
        Deletes a shipper passing their id.

        Args:
            session (Session): The SQLModel session to interact with the database.
            shipper_id (int): The shipper's id.

        Returns:
            ShipperPublic: A ShipperPublic object.
        """

        # Get the shipper to delete
        shipper_to_delete = session.get(Shipper, shipper_id)

        # Raise exception if shipper_id couldn't get a shipper
        if not shipper_to_delete:
            raise ShipperNotFoundError(shipper_id=shipper_id)
        
        # Delete the shipper
        session.delete(shipper_to_delete)
        session.commit()

        # Return the shipper public
        return ShipperPublic.model_validate(shipper_to_delete)

    ###############################################################################################

###################################################################################################