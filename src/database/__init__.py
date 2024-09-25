from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create an SQLite database and establish a connection
engine = create_engine('sqlite:///gadisi.db', echo=True)

# Define a base class for declarative models
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

