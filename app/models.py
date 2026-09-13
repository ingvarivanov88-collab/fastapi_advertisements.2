from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # user или admin
    created_at = Column(DateTime, default=datetime.utcnow)

    advertisements = relationship("Advertisement", back_populates="author_obj")

class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    author_obj = relationship("User", back_populates="advertisements")