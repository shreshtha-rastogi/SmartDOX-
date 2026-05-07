from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime

# Database file ka path
DATABASE_URL = "sqlite:///./smartdox.db"

# Engine create karna
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SessionLocal (Yahi missing tha!)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# 1. User Table Model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    mobile = Column(String)
    password = Column(String)

# 2. History Table Model
class FileHistory(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

# Tables create karne ka function
def create_db():
    Base.metadata.create_all(bind=engine)