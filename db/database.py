
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists
load_dotenv()
def get_db_url(): return os.getenv("DATABASE_URL")
def database_ready():
    url=get_db_url()
    return url is not None and database_exists(url)
def get_engine():
    return create_engine(get_db_url())
def get_session():
    return sessionmaker(autocommit=False,autoflush=False,bind=get_engine())()
