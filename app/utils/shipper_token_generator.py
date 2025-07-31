###########################
# SHIPPER TOKEN GENERATOR #
###########################


###################################################################################################
# Imports

import random

###################################################################################################


###################################################################################################

def shipper_token_generator() -> int:
    
    """
    Creates a random 4-digit shipper token to assign to a order

    """
    shipper_token = random.randint(1000, 9999)
    return shipper_token

###################################################################################################


###################################################################################################

def verify_shipper_token(given_token: int, db_token: int) -> bool:
    """
    Verifies the token given for the client with the generated token at the moment the order was
    created.

    Args:
        given_token: The token that the client give to the shipper.
        db_token: The stored token.
    
    Returns:
        bool: True if the token is verified, False if not.
    """

    return given_token == db_token

###################################################################################################
