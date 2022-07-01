from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import environ


uri = environ.get("SQLALCHEMY_DATABASE_URI")
#uri = environ.get("DATABASE_URL")
engine = create_engine(uri)
Session = sessionmaker(engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(engine)
