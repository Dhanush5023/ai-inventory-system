from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from ..core.config import settings

# Database engine
# Database engine
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database Models

class User(Base):
    """User authentication model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String(50), default="user") # admin, user, customer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sales = relationship("Sale", back_populates="user")
    orders = relationship("Order", back_populates="user")


class Product(Base):
    """Product inventory model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100), index=True)
    description = Column(Text)
    unit_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    current_stock = Column(Integer, default=0)
    minimum_stock = Column(Integer, default=10)
    maximum_stock = Column(Integer, default=1000)
    unit = Column(String(50), default="pcs")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="products")
    sales = relationship("Sale", back_populates="product")
    predictions = relationship("Prediction", back_populates="product")
    alerts = relationship("Alert", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class Sale(Base):
    """Sales transaction model"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    sale_date = Column(DateTime, default=datetime.utcnow, index=True)
    notes = Column(Text)
    
    # Relationships
    product = relationship("Product", back_populates="sales")
    user = relationship("User", back_populates="sales")


class Supplier(Base):
    """Supplier information model"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    rating = Column(Float, default=5.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="supplier")
    orders = relationship("Order", back_populates="supplier")


class Order(Base):
    """Purchase order model"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(100), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50), default="pending", index=True) # pending, approved, shipped, received, cancelled
    total_amount = Column(Float, default=0.0)
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_delivery = Column(DateTime)
    received_date = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="orders")
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Purchase order items"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Prediction(Base):
    """ML prediction results model"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    prediction_date = Column(DateTime, default=datetime.utcnow, index=True)
    target_date = Column(DateTime, nullable=False, index=True)
    predicted_demand = Column(Float, nullable=False)
    confidence_score = Column(Float)
    model_used = Column(String(100))
    recommended_stock = Column(Integer)
    
    # Relationships
    product = relationship("Product", back_populates="predictions")


class Alert(Base):
    """Automated restock alerts model"""
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    alert_type = Column(String(50), nullable=False) # low_stock, restock_needed, out_of_stock
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="medium") # low, medium, high, critical
    recommended_quantity = Column(Integer)
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime)
    
    # Relationships
    product = relationship("Product", back_populates="alerts")


# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
