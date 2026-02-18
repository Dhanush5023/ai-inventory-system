import pandas as pd
import numpy as np
from typing import Tuple, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ...models.database import Sale, Product


class DataLoader:
    """Load and prepare data from database for ML models"""

    @staticmethod
    def load_sales_history(
        db: Session,
        product_id: int,
        days_back: int = 365
    ) -> pd.DataFrame:
        """Load sales history for a specific product"""
        start_date = datetime.utcnow() - timedelta(days=days_back)

        sales = db.query(Sale).filter(
            Sale.product_id == product_id,
            Sale.sale_date >= start_date
        ).order_by(Sale.sale_date).all()

        if not sales:
            # Return empty dataframe with expected structure
            return pd.DataFrame(columns=['date', 'quantity', 'amount'])

        # Convert to DataFrame
        data = []
        for sale in sales:
            data.append({
                'date': sale.sale_date.date(),
                'quantity': sale.quantity,
                'amount': sale.total_amount,
                'unit_price': sale.unit_price,
            })

        df = pd.DataFrame(data)

        # Aggregate by date
        df_agg = df.groupby('date').agg({
            'quantity': 'sum',
            'amount': 'sum',
            'unit_price': 'mean'
        }).reset_index()

        return df_agg

    @staticmethod
    def load_all_products_sales(
        db: Session,
        days_back: int = 365
    ) -> pd.DataFrame:
        """Load sales history for all products"""
        start_date = datetime.utcnow() - timedelta(days=days_back)

        sales = db.query(Sale).filter(
            Sale.sale_date >= start_date
        ).join(Product).all()

        data = []
        for sale in sales:
            data.append({
                'date': sale.sale_date.date(),
                'product_id': sale.product_id,
                'product_name': sale.product.name if sale.product else 'Unknown',
                'category': sale.product.category if sale.product else 'Unknown',
                'quantity': sale.quantity,
                'amount': sale.total_amount,
                'unit_price': sale.unit_price,
            })

        return pd.DataFrame(data)

    @staticmethod
    def get_product_info(db: Session, product_id: int) -> dict:
        """Get product information"""
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return None

        return {
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'category': product.category,
            'unit_price': product.unit_price,
            'cost_price': product.cost_price,
            'current_stock': product.current_stock,
            'minimum_stock': product.minimum_stock,
            'maximum_stock': product.maximum_stock,
        }
