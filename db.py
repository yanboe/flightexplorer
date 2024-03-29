from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from os import environ

uri = environ.get("DATABASE_URL").replace("postgres://", "postgresql://")
engine = create_engine(uri)
Session = sessionmaker(engine)
Base = declarative_base()


def init_db():
    Base.metadata.create_all(engine)
