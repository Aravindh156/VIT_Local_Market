from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import DateTime
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String)  # customer, retailer, admin
    password = Column(String)
    status = Column(String, default="active")  # <-- MUST be added!


class Retailer(Base):
    __tablename__ = "retailers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    location = Column(String)
    name = Column(String)
    deliverable = Column(Boolean, default=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"))
    name = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    category = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    retailer_id = Column(Integer, ForeignKey("retailers.id"))
    product = Column(String)
    quantity = Column(Integer)
    total_price = Column(Float)
    status = Column(String, default="Pending")  # 'Pending', 'Confirmed'

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"))
    message = Column(String)
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# status = Column(String, default="active")  # 'active', 'pending', 'rejected'
