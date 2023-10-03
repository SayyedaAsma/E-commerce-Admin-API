from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum,VARCHAR
from sqlalchemy.orm import relationship
#from sqlalchemy.ext.declarative import declarative_base
from database import Base
from datetime import datetime 
import enum

#Base = declarative_base()


# Product Table
class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR(50), index=True, nullable=False)
    description = Column(VARCHAR(100))
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    inventory = relationship("Inventory", back_populates="product")
    sales = relationship("Sale", back_populates="product")
    InventoryChangeLog = relationship("InventoryChangeLog", back_populates="product")




# Sale Table
class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    sale_date = Column(DateTime)

    product = relationship("Product", back_populates="sales")


# Inventory Table
class Inventory(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    last_updated = Column(DateTime)


    product = relationship("Product", back_populates="inventory")


# Category Table
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(VARCHAR(50), index=True, nullable=False)


# InventoryChangeLog Table
class InventoryChangeLog(Base):
    __tablename__ = 'inventory_change_logs'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity_change = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="InventoryChangeLog")


   
