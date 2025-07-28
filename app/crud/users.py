################################
#       CRUD for Users        #
################################


###################################################################################################
# Imports

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.auth.hashing import hash_password
from app.models.users import User, UserAddress
from app.schemas.users import (
    UserCreate, CreateUserAddress, UserUpdate, UserAddressUpdate, UserPublic, UserAddressPublic,
    FullUserPublic
)


###################################################################################################


###################################################################################################
# CRUD

class UsersCrud():

    ###############################################################################################
    # Create

    def create_user(session: Session, user_create: UserCreate) -> UserPublic | None:
        
        """
        Creates a new user in database by passing the user information (firstname, lastname, dni, 
        email, password, role and optionally a shipper_id if the user is a shipper).
        The method gets the plain password passed for the user and using hash_password makes a
        secure password.

        Args:
            session (Session): The SQLModel session to interact with the database.
            user_create (UserCreate): Data to create a new user.
        
        Returns:
            A UserPublic or None if there was any problem, like an existing email or dni number
        """
        
        # Get the plain password from user_create
        plain_password = user_create.password

        # Hash the password
        hashed_password = hash_password(plain_password=plain_password)

        # Generate the object User (database model)
        user_db = User(
            firstname=user_create.firstname,
            lastname=user_create.lastname,
            user_dni=user_create.user_dni,
            user_email=user_create.user_email,
            hash_password=hashed_password,
            role=user_create.role,
            shipper_id=user_create.shipper_id
        )

        # Add the user to the database
        try:
            session.add(user_db)
            session.commit()
            session.refresh(user_db)

            # Generate a UserPublic for the response
            user_public = UserPublic.model_validate(user_db)

            # Return the UserPublic
            return user_public

        except IntegrityError:
            # Rollback if there's an integrity error (existing email, dni, etc..)
            session.rollback()
            return None


    @staticmethod
    def create_user_address(
        session: Session, 
        user_id: int, 
        user_address: CreateUserAddress
    ) -> UserAddress | None:
        
        """
        Adds address information of a user, passing their phone number, address, city, province,
        etc.

        Args:
            session (Session): The SQLModel session to interact with the database.
            user_id (int): The user's id.
            user_address (CreateUserAddress): Information of the user's address.
        
        Returns:
            A UserAddress object or None if user_id couldn't match any user.
        """

        # Find a User with the user_id, return None if there's no user
        user = session.get(User, user_id)

        if not user:
            return None
        
        # Create and return an user address
        useraddress_db = UserAddress.model_validate(user_address)
        session.add(useraddress_db)
        session.commit()
        session.refresh(useraddress_db)

        return useraddress_db

    ###############################################################################################


    ###############################################################################################
    # Read
    
    @staticmethod
    def get_user_by_dni(session: Session, user_dni: int) -> FullUserPublic | None:

        """
        Gets a user's information passing their dni number.
        
        Args:
            session (Session): The SQLModel session to interact with the database.
            user_dni (int): The user's dni number.
        
        Returns:
            A FullUserPublic object or None if the dni couldn't match any user.
        """

        # Get the user
        user = session.exec(
            select(User)
            .options(selectinload(User.user_address))
            .where(User.user_dni == user_dni)
        ).first()

        # Return None if there is no user with the user_dni
        if not user:
            return None
        
        # Get the user's address
        user_address = user.user_address

        # Generate a UserAddressPublic
        user_address_public = UserAddressPublic.model_validate(user_address)

        # Generate and return the FullUserPublic
        full_user_public = FullUserPublic(
            user_id=user.user_id,
            firstname=user.firstname,
            lastname=user.lastname,
            user_dni=user.user_dni,
            user_email=user.user_email,
            is_active=user.is_active,
            address=user_address_public
        )

        return full_user_public


    @staticmethod
    def get_user_by_email(session: Session, user_email: str) -> FullUserPublic | None:

        """
        Gets a user's information passing their email.
        
        Args:
            session (Session): The SQLModel session to interact with the database.
            user_email (str): The user's email.
        
        Returns:
            A FullUserPublic object or None if the email couldn't match any user.
        """

        # Get the user
        user = session.exec(
            select(User)
            .options(selectinload(User.user_address))
            .where(User.user_email == user_email)
        ).first()

        # Return None if there is no user with the user_email
        if not user:
            return None
        
        # Get the user's address
        user_address = user.user_address

        # Generate a UserAddressPublic
        user_address_public = UserAddressPublic.model_validate(user_address)

        # Generate and return the FullUserPublic
        full_user_public = FullUserPublic(
            user_id=user.user_id,
            firstname=user.firstname,
            lastname=user.lastname,
            user_dni=user.user_dni,
            user_email=user.user_email,
            is_active=user.is_active,
            address=user_address_public
        )

        return full_user_public

    ###############################################################################################


    ###############################################################################################
    # Update

    @staticmethod
    def update_user(
        session: Session,
        user_id: int, 
        user_update: UserUpdate
    ) -> UserPublic | None:
        
        """
        Updates a user's information, like firstname, lastname or password.
        
        Args:
            session (Session): The SQLModel session to interact with the database.
            user_id: The user's id.
            user_update (UserUpdate): Data of the user to be modified.
        
        Returns:
            A UserPublic object or None if the user_id couldn't match any user.
        """

        # Get the user to update
        user_to_update = session.get(User, user_id)

        # Return None if there's no User with the user_id
        if not user_to_update:
            return None
        
        # Update the user
        user_to_update.sqlmodel_update(user_update)
        session.add(user_to_update)
        session.commit()
        session.refresh(user_to_update)

        # Generate and return a UserPublic
        user_public = UserPublic.model_validate(user_to_update)

        return user_public


    @staticmethod
    def update_user_address(
        session: Session, 
        user_id: int, 
        address_update: UserAddressUpdate
    ) -> UserAddressPublic | None:
        
        """
        Updates a user's address passing the fields to be modified, like phone number, address, city,
        province or apartment info.

        Args:
            session (Session): The SQLModel session to interact with the database.
            user_id (int): The user's id.
            address_update (UserAddressUpdate): Data of the address to be updated.
        
        Returns:
            A UserAddressPublic object or None if there is no address information asociated at the user_id
        """
        
        # Get the address with user_id
        user_address = session.exec(
            select(UserAddress).where(UserAddress.user_id == user_id)
        ).first()

        # Return None if there's no address asociated to that user_id
        if not user_address:
            return None
        
        # Update the user information
        user_address.sqlmodel_update(address_update)
        session.add(user_address)
        session.commit()
        session.refresh(user_address)

        # Create and return the UserAddressPublic
        user_address_public = UserAddressPublic.model_validate(user_address)

        return user_address_public


    @staticmethod
    def deactivate_user(session: Session, user_id: int) -> UserPublic | None:

        """
        Makes a passive delete of a user, turning is_active field to False.

        Args:
            session (Session): The SQLModel session to interact with the database.
            user_id (int): The user's id.
        
        Returns:
            A UserPublic or None if user_id couldn't match any user.
        """

        # Gets the user
        user = session.get(User, user_id)

        # Return None if user_id couldn't find a user
        if not user:
            return None
        
        # Update the is_active field
        user.is_active = False

        # Commit changes
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create and return a UserPublic
        user_public = UserPublic.model_validate(user)

        return user_public


    @staticmethod
    def reactivate_user(session: Session, user_id: int) -> UserPublic | None:

        """
        Reactivates a user updating the is_active field to True.

        Args:
            session (Session): The SQLModel session to interact with the database.
            user_id (int): The user's id.
        
        Returns:
            A UserPublic or None if user_id couldn't match any user.
        """

        # Gets the user
        user = session.get(User, user_id)

        # Return None if user_id couldn't find a user
        if not user:
            return None
        
        # Update the is_active field
        user.is_active = True

        # Commit changes
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create and return a UserPublic
        user_public = UserPublic.model_validate(user)

        return user_public
    ###############################################################################################

###################################################################################################