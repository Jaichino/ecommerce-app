################################
#      CRUD for Shippers       #
################################


###################################################################################################
# Imports

from sqlmodel import Session, select
from app.models.shippers import Shipper
from app.schemas.shippers import ShipperCreate, ShipperPublic, ShipperUpdate

###################################################################################################


###################################################################################################
# CRUD

class ShippersCrud():

    ###############################################################################################
    # Create

    @staticmethod
    def create_shipper(session: Session, shipper_create: ShipperCreate) -> Shipper:
        """
        Creates a new shipper by passing shipper data like name, email and phone number.

        Args:
            session (Session): The SQLModel session to interact with the database.
            shipper (ShipperCreate): Data of the shipper.

        Returns:
            Shipper: A shipper object.
        """

        # Validate the ShipperCreate as a Shipper
        shipper_db = Shipper.model_validate(shipper_create)

        # Create the shipper and return it
        session.add(shipper_db)
        session.commit()
        session.refresh(shipper_db)

        return shipper_db


    ###############################################################################################


    ###############################################################################################
    # Read

    @staticmethod
    def get_shipper_by_id(session: Session, shipper_id: int) -> Shipper | None:
        """
        Gets a shipper by passing their id.

        Args:
            session (Session): The SQLModel session to interact with the database.
            shipper_id (int): The shipper's id.

        Returns:
            A Shipper object or None if the shipper_id couldn't match any shipper.
        """

        # Get the shipper
        shipper = session.get(Shipper, shipper_id)

        # Return None if shipper_id couldn't find a shipper
        if not shipper:
            return None

        # Return the shipper
        return shipper


    @staticmethod
    def get_shippers(session: Session) -> list[Shipper] | None:
        """
        Gets the full list of shippers.

        Args:
            session (Session): The SQLModel session to interact with the database.

        Returns:
            A list of Shipper objects or None if there is no shipper.
        """

        # Get the shippers
        shippers = session.exec(select(Shipper).order_by(Shipper.shipper_name)).all()

        # Return None if there's no shipper
        if not shippers:
            return None

        # Return the shippers
        return shippers

    ###############################################################################################


    ###############################################################################################
    # Update

    @staticmethod
    def update_shipper(
        session: Session, shipper_id: int, shipper_update: ShipperUpdate
    ) -> Shipper | None:
        """
        Updates a shipper passing their id and the fields to be modified, like their name, email
        and phone number.

        Args:
            session (Session): The SQLModel session to interact with the database.
            shipper_id (int): The shipper's id.
            shipper_update (ShipperUpdate): Data of the shipper to be modified.

        Returns:
            A Shipper object or None if the shipper_id couldn't match any shipper.
        """

        # Get the shipper to be updated
        shipper_to_update = session.get(Shipper, shipper_id)

        # Return None if shipper_id couldn't get a shipper
        if not shipper_to_update:
            return None
        
        # Update and return the shipper
        shipper_to_update.sqlmodel_update(shipper_update)
        session.add(shipper_to_update)
        session.commit()
        session.refresh(shipper_to_update)

        return shipper_to_update

    ###############################################################################################


    ###############################################################################################
    # Delete

    @staticmethod
    def delete_shipper(session: Session, shipper_id: int) -> Shipper:
        """
        Deletes a shipper passing their id.

        Args:
            session (Session): The SQLModel session to interact with the database.
            shipper_id (int): The shipper's id.

        Returns:
            A Shipper object or None if the shipper_id couldn't match any shipper.
        """

        # Get the shipper to delete
        shipper_to_delete = session.get(Shipper, shipper_id)

        # Return None if shipper_id couldn't get a shipper
        if not shipper_to_delete:
            return None
        
        # Delete and return the shipper
        session.delete(shipper_to_delete)
        session.commit()

        return shipper_to_delete

    ###############################################################################################

###################################################################################################