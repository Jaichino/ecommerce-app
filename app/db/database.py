#######################
# DATABASE CONNECTION #
#######################

###################################################################################################
# Imports

import os
from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
###################################################################################################


###################################################################################################
# Database credentials

# Get the .env path
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Get DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_DEV_URL") # <---- Change to DATABASE_URL in production
###################################################################################################


###################################################################################################
# Database engine

engine = create_engine(DATABASE_URL, echo=True)
###################################################################################################


###################################################################################################
# Session maker
def get_session():
    with Session(engine) as session:
        yield session
###################################################################################################


###################################################################################################
# Database creation function

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
###################################################################################################