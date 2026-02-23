"""
Database Seed Script
Generates demo data for the inventory system
"""

import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.database import (
    User, Product, Supplier, Sale, Order, OrderItem,
    Prediction, Alert, engine, SessionLocal, init_db
)
from app.core.security import get_password_hash


# Sample data
CATEGORIES = [
    'Consumer Electronics', 'FMCG & Groceries', 'Textiles & Apparel', 
    'Home & Kitchen', 'Industrial & Hardware', 'Stationery & Office', 'Personal Care'
]

PRODUCT_NAMES = {
    'Consumer Electronics': [
        'Bajaj Ceiling Fan', 'Orient Electric Table Fan', 'Havells 9W LED Bulb', 
        'Crompton Exhaust Fan', 'SYSKA 20000mAh Power Bank', 'Boat Rockerz 450 Headphones', 
        'Noise ColorFit Smartwatch', 'Zebronics Bluetooth Speaker', 'Voltas 1.5 Ton AC', 
        'Blue Star Water Purifier', 'Mi Smart TV 43 inch', 'Samsung Galaxy M Series',
        'Intex Multimedia Speakers', 'V-Guard Voltage Stabilizer', 'Usha Iron Box'
    ],
    'FMCG & Groceries': [
        'Amul Butter 500g', 'Maggi Masala Noodles 12pk', 'Tata Tea Gold 1kg', 
        'Parle-G Biscuits Family Pack', 'Britannia Good Day Cookies', 'Haldiram\'s Alu Bhujia', 
        'Aashirvaad Whole Wheat Atta 5kg', 'Saffola Gold Cooking Oil 5L', 'Dabur Honey 500g', 
        'Catch Turmeric Powder', 'Everest Garam Masala', 'Mother\'s Recipe Mango Pickle',
        'MTR Poha Ready-to-eat', 'Fortune Soyabean Oil', 'Priya Mixed Veg Pickle',
        'India Gate Basmati Rice 5kg', 'Tata Salt 1kg', 'Brook Bond Red Label Tea'
    ],
    'Textiles & Apparel': [
        'Monte Carlo Woolen Sweater', 'Peter England Formal Shirt', 'Westside Ethnic Kurti', 
        'Fabindia Cotton Saree', 'Manyavar Wedding Sherwani', 'Jockey Men\'s Cotton Tee', 
        'Roadster Slim Fit Jeans', 'Biba Women\'s Salwar Kameez', 'Wildcraft Trekking Backpack', 
        'Sparx Sports Sandals', 'Liberty Formal Shoes', 'Bata Leather Belt',
        'Raymond Suit Length', 'Van Heusen Trousers', 'Levi\'s 511 Jeans'
    ],
    'Home & Kitchen': [
        'Prestige Induction Cooktop', 'Hawkins Contura Pressure Cooker', 'Milton Thermosteel Bottle', 
        'Butterfly Mixie 3 Jar', 'Pigeon Non-Stick Tawa', 'Eveready Flashlight', 
        'Bajaj Majesty Toaster', 'Usha Sewing Machine', 'Godrej Interio Wardrobe',
        'Sleepwell Foam Mattress', 'Nilkamal Plastic Chair', 'Borosil Glass Set'
    ],
    'Industrial & Hardware': [
        'Asian Paints Tractor Emulsion 20L', 'Berger Wall Primer 10L', 'Pidilite Fevicol SH 1kg', 
        'JK Super Cement 50kg', 'UltraTech Cement OPC', 'Havells Modular Switches', 
        'Polycab Copper Wires 90m', 'Astral PVC Pipes', 'Somany Bathroom Tiles', 
        'Kajaria Floor Ceramics', 'Tata Tiscon Steel Rods', 'Godrej Nav-Tal Lock'
    ],
    'Stationery & Office': [
        'Classmate Notebook A4', 'Camel Artist Watercolor Set', 'Nataraj 621 Pencil Box', 
        'Cello Butterflow Blue Pens 10pk', 'Kangaro HP-45 Stapler', 'Faber-Castell Connector Pens', 
        'Presto Self-Inking Stamp', 'JK Copier Paper Rim', 'Navneet Journal Set',
        'Parker Vector Fountain Pen', 'Linc Pentonic Black Pens', 'ITC Classmate Geometry Box'
    ],
    'Personal Care': [
        'Patanjali Aloe Vera Gel', 'Colgate Swarna Vedshakti 200g', 'Lux International Soap', 
        'Surf Excel Matic Liquid', 'Vim Dishwash Bar 500g', 'Dettol Antiseptic Liquid',
        'Himalaya Neem Face Wash', 'Parachute Coconut Oil 500ml', 'Fair & Lovely Cream',
        'Sensodyne Toothpaste', 'Lifebuoy Hand Wash', 'Pears Soft Soap'
    ]
}

SUPPLIERS = [
    {'name': 'Bharat Electronics Ltd', 'contact_person': 'Rajesh Kumar', 'email': 'rajesh@bharatelelec.in', 'phone': '+91-98765-43210', 'city': 'Bangalore', 'country': 'India', 'rating': 4.9},
    {'name': 'Tata Steel & Hardware', 'contact_person': 'Amit Sharma', 'email': 'amit@tatasteel.co.in', 'phone': '+91-98220-11223', 'city': 'Mumbai', 'country': 'India', 'rating': 4.7},
    {'name': 'Godrej Office Solutions', 'contact_person': 'Priya Singh', 'email': 'priya@godrej.com', 'phone': '+91-91234-56789', 'city': 'Pune', 'country': 'India', 'rating': 4.6},
    {'name': 'Reliance Retail Hub', 'contact_person': 'Vikram Mehta', 'email': 'vikram@reliance.in', 'phone': '+91-99887-76655', 'city': 'Delhi', 'country': 'India', 'rating': 4.8},
    {'name': 'Wipro Technologies Supplies', 'contact_person': 'Sunita Rao', 'email': 'sunita@wipro.com', 'phone': '+91-94455-66778', 'city': 'Hyderabad', 'country': 'India', 'rating': 4.5},
    {'name': 'Mahindra Logistics Services', 'contact_person': 'Sanjay Gupta', 'email': 'sanjay@mahindra.in', 'phone': '+91-93344-55667', 'city': 'Chennai', 'country': 'India', 'rating': 4.7},
]


def create_users(db: Session):
    """Create demo users"""
    users = [
        User(
            email='admin@inventory.com',
            username='admin',
            hashed_password=get_password_hash('admin123'),
            full_name='Admin User',
            is_admin=True,
            role='admin',
            is_active=True
        ),
        User(
            email='manager@inventory.com',
            username='manager',
            hashed_password=get_password_hash('manager123'),
            full_name='Manager User',
            is_admin=False,
            role='manager',
            is_active=True
        ),
        User(
            email='customer@inventory.com',
            username='customer',
            hashed_password=get_password_hash('customer123'),
            full_name='Customer User',
            is_admin=False,
            role='customer',
            is_active=True
        ),
    ]
    
    db.add_all(users)
    db.commit()
    print(f"[OK] Created {len(users)} users")
    return users


def create_suppliers(db: Session):
    """Create demo suppliers"""
    suppliers = []
    for supplier_data in SUPPLIERS:
        supplier = Supplier(**supplier_data)
        suppliers.append(supplier)
    
    db.add_all(suppliers)
    db.commit()
    print(f"[OK] Created {len(suppliers)} suppliers")
    return suppliers


def create_products(db: Session, suppliers: list):
    """Create demo products"""
    products = []
    product_id = 1
    
    for category, names in PRODUCT_NAMES.items():
        for name in names:
            sku = f"SKU{product_id:04d}"
            # Adjusted for Indian Rupee (INR) values
            unit_price = round(random.uniform(500, 50000), 2)
            cost_price = round(unit_price * random.uniform(0.6, 0.85), 2)
            
            product = Product(
                name=name,
                sku=sku,
                category=category,
                description=f"High-quality {name.lower()} for professional use",
                unit_price=unit_price,
                cost_price=cost_price,
                current_stock=random.randint(0, 200),
                minimum_stock=random.randint(10, 30),
                maximum_stock=random.randint(100, 500),
                unit='pcs',
                supplier_id=random.choice(suppliers).id
            )
            products.append(product)
            product_id += 1
    
    db.add_all(products)
    db.commit()
    print(f"[OK] Created {len(products)} products")
    return products


def create_sales(db: Session, products: list, users: list):
    """Create historical sales data (6 months)"""
    sales = []
    start_date = datetime.utcnow() - timedelta(days=180)
    
    for product in products:
        # Create varying sales patterns
        num_sales = random.randint(20, 100)
        
        for _ in range(num_sales):
            # Generate a date within the last 180 days, but not in the future
            delay_seconds = random.randint(0, 180 * 24 * 3600)
            sale_date = datetime.utcnow() - timedelta(seconds=delay_seconds)
            
            quantity = random.randint(1, 20)
            # Add some price variation
            unit_price = product.unit_price * random.uniform(0.95, 1.05)
            
            sale = Sale(
                product_id=product.id,
                user_id=random.choice(users).id,
                quantity=quantity,
                unit_price=round(unit_price, 2),
                total_amount=round(quantity * unit_price, 2),
                sale_date=sale_date,
                notes=f"Sale transaction for {product.name}"
            )
            sales.append(sale)
    
    db.add_all(sales)
    db.commit()
    print(f"[OK] Created {len(sales)} sales records")
    return sales


def create_orders(db: Session, suppliers: list, products: list, users: list):
    """Create sample purchase orders"""
    orders = []
    
    for i in range(15):
        order_date = datetime.utcnow() - timedelta(days=random.randint(1, 60))
        
        order = Order(
            order_number=f"PO{datetime.now().year}{i+1:04d}",
            supplier_id=random.choice(suppliers).id,
            user_id=random.choice(users).id,
            status=random.choice(['pending', 'approved', 'shipped', 'received']),
            order_date=order_date,
            expected_delivery=order_date + timedelta(days=random.randint(7, 30)),
            notes=f"Purchase order #{i+1}"
        )
        
        # Add order items
        num_items = random.randint(2, 8)
        selected_products = random.sample(products, num_items)
        total_amount = 0
        
        db.add(order)
        db.flush()  # Get order ID
        
        for product in selected_products:
            quantity = random.randint(10, 100)
            unit_price = product.cost_price
            total_price = quantity * unit_price
            total_amount += total_price
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=round(unit_price, 2),
                total_price=round(total_price, 2)
            )
            db.add(order_item)
        
        order.total_amount = round(total_amount, 2)
        orders.append(order)
    
    db.commit()
    print(f"[OK] Created {len(orders)} purchase orders")
    return orders


def create_alerts(db: Session, products: list):
    """Create sample alerts for low stock items"""
    alerts = []
    
    for product in products:
        if product.current_stock <= product.minimum_stock:
            severity = 'critical' if product.current_stock == 0 else 'high' if product.current_stock < product.minimum_stock * 0.5 else 'medium'
            alert_type = 'out_of_stock' if product.current_stock == 0 else 'low_stock'
            
            alert = Alert(
                product_id=product.id,
                alert_type=alert_type,
                message=f"Stock level for {product.name} is {'OUT' if product.current_stock == 0 else 'LOW'} ({product.current_stock} units)",
                severity=severity,
                recommended_quantity=product.maximum_stock - product.current_stock,
                is_read=random.choice([True, False]),
                is_resolved=False,
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7))
            )
            alerts.append(alert)
    
    db.add_all(alerts)
    db.commit()
    print(f"[OK] Created {len(alerts)} alerts")
    return alerts


def seed_database():
    """Main seeding function"""
    print("\n" + "="*50)
    print("Starting database seeding...")
    print("="*50 + "\n")
    
    db = SessionLocal()
    
    try:
        # Initialize tables
        print("Dropping existing tables...")
        from app.models.database import Base
        Base.metadata.drop_all(bind=engine)
        print("Initializing database tables...")
        init_db()
        print("[OK] Database initialized")

        # Clear existing data
        print("Clearing existing data...")
        db.query(Alert).delete()
        db.query(Prediction).delete()
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(Sale).delete()
        db.query(Product).delete()
        db.query(Supplier).delete()
        db.query(User).delete()
        db.commit()
        print("[OK] Database cleared\n")
        
        # Create data
        users = create_users(db)
        suppliers = create_suppliers(db)
        products = create_products(db, suppliers)
        sales = create_sales(db, products, users)
        orders = create_orders(db, suppliers, products, users)
        alerts = create_alerts(db, products)
        
        print("\n" + "="*50)
        print("Database seeding completed successfully!")
        print("="*50)
        print("\nLogin Credentials:")
        print("-" * 50)
        print("Admin:   email: admin@inventory.com    password: admin123")
        print("Manager: email: manager@inventory.com  password: manager123")
        print("Customer: email: customer@inventory.com password: customer123")
        print("-" * 50 + "\n")
        
    except Exception as e:
        print(f"\n[X] Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
