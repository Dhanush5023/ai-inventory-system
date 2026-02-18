"""
Prediction Service
Handles demand forecasting and stock recommendations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
import joblib
import os

from ...models.database import Product, Sale, Prediction
from .model_trainer import DemandPredictor
from ...core.config import settings


class PredictionService:
    """Service for generating demand predictions"""
    
    def __init__(self, model_path: str = "./models"):
        self.predictor = DemandPredictor(model_path)
        self.predictor.load_models()
        
        # Load model metrics if available
        try:
            metrics_file = os.path.join(model_path, 'model_metrics.pkl')
            self.model_metrics = joblib.load(metrics_file)
        except:
            self.model_metrics = {}
    
    def generate_predictions(self, db: Session, product_id: int, 
                           days_ahead: int = 30) -> List[Prediction]:
        """
        Generate demand predictions for a product
        
        Args:
            db: Database session
            product_id: Product ID
            days_ahead: Number of days to predict ahead
        
        Returns:
            List of Prediction objects
        """
        # Get product
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return []
        
        # Get historical sales data
        sales_query = db.query(Sale).filter(
            Sale.product_id == product_id
        ).order_by(Sale.sale_date.asc())
        
        sales_data = []
        for sale in sales_query:
            sales_data.append({
                'sale_date': sale.sale_date,
                'quantity': sale.quantity,
                'product_id': sale.product_id,
                'unit_price': sale.unit_price
            })
        
        if len(sales_data) < 30:  # Need minimum data
            return self._generate_simple_prediction(db, product, days_ahead)
        
        df = pd.DataFrame(sales_data)
        
        # Prepare features
        X, _ = self.predictor.prepare_features(df)
        
        # Generate predictions for future dates
        predictions = []
        last_date = df['sale_date'].max()
        
        for i in range(1, days_ahead + 1):
            target_date = last_date + timedelta(days=i)
            
            # Create feature vector for target date
            features = self._create_feature_vector(df, target_date, product_id)
            
            # Get prediction
            predicted_demand, confidence = self.predictor.predict_ensemble(
                pd.DataFrame([features])
            )
            
            # Calculate recommended stock
            recommended_stock = self._calculate_recommended_stock(
                predicted_demand, 
                product.minimum_stock,
                confidence
            )
            
            # Determine best model
            best_model = max(
                self.model_metrics.items(),
                key=lambda x: x[1].get('accuracy', 0)
            )[0] if self.model_metrics else 'ensemble'
            
            # Create prediction record
            prediction = Prediction(
                product_id=product_id,
                prediction_date=datetime.utcnow(),
                target_date=target_date,
                predicted_demand=round(predicted_demand, 2),
                confidence_score=round(confidence, 2),
                model_used=best_model,
                recommended_stock=int(recommended_stock)
            )
            
            predictions.append(prediction)
        
        return predictions
    
    def _create_feature_vector(self, df: pd.DataFrame, target_date: datetime,
                               product_id: int) -> Dict:
        """Create feature vector for a specific date"""
        features = {}
        
        # Time-based features
        features['day_of_week'] = target_date.weekday()
        features['day_of_month'] = target_date.day
        features['month'] = target_date.month
        features['quarter'] = (target_date.month - 1) // 3 + 1
        features['week_of_year'] = target_date.isocalendar()[1]
        
        # Get recent sales for lag features
        recent_sales = df.tail(30)['quantity'].values
        
        features['lag_1'] = recent_sales[-1] if len(recent_sales) >= 1 else 0
        features['lag_7'] = recent_sales[-7] if len(recent_sales) >= 7 else 0
        features['lag_30'] = recent_sales[-30] if len(recent_sales) >= 30 else 0
        
        # Rolling statistics
        features['rolling_mean_7'] = np.mean(recent_sales[-7:]) if len(recent_sales) >= 7 else 0
        features['rolling_mean_30'] = np.mean(recent_sales[-30:]) if len(recent_sales) >= 30 else 0
        features['rolling_std_7'] = np.std(recent_sales[-7:]) if len(recent_sales) >= 7 else 0
        
        return features
    
    def _calculate_recommended_stock(self, predicted_demand: float,
                                    minimum_stock: int,
                                    confidence: float) -> int:
        """
        Calculate recommended stock level
        
        Factors in:
        - Predicted demand
        - Safety stock
        - Confidence level
        """
        # Base on predicted demand for next 7 days (restock threshold)
        base_stock = predicted_demand * settings.RESTOCK_THRESHOLD_DAYS
        
        # Add safety stock (inversely proportional to confidence)
        safety_factor = (100 - confidence) / 100
        safety_stock = base_stock * safety_factor * 0.5
        
        # Ensure at least minimum stock
        recommended = max(base_stock + safety_stock, minimum_stock)
        
        return int(np.ceil(recommended))
    
    def _generate_simple_prediction(self, db: Session, product: Product,
                                   days_ahead: int) -> List[Prediction]:
        """
        Generate simple predictions when insufficient data
        Uses average of available data or product minimum stock
        """
        # Get available sales data
        sales_query = db.query(Sale).filter(
            Sale.product_id == product.id
        ).order_by(Sale.sale_date.desc()).limit(90)
        
        sales = list(sales_query)
        
        if sales:
            avg_daily_demand = sum(s.quantity for s in sales) / len(sales)
        else:
            avg_daily_demand = product.minimum_stock / 7  # Estimate based on min stock
        
        predictions = []
        today = datetime.utcnow().date()
        
        for i in range(1, days_ahead + 1):
            target_date = today + timedelta(days=i)
            
            prediction = Prediction(
                product_id=product.id,
                prediction_date=datetime.utcnow(),
                target_date=datetime.combine(target_date, datetime.min.time()),
                predicted_demand=round(avg_daily_demand, 2),
                confidence_score=40.0,  # Low confidence for simple predictions
                model_used='simple_average',
                recommended_stock=int(avg_daily_demand * settings.RESTOCK_THRESHOLD_DAYS)
            )
            
            predictions.append(prediction)
        
        return predictions
    
    def generate_all_predictions(self, db: Session, 
                                days_ahead: int = 30) -> Dict[str, int]:
        """
        Generate predictions for all active products
        
        Returns:
            Statistics about generated predictions
        """
        products = db.query(Product).all()
        
        stats = {
            'total_products': len(products),
            'predictions_generated': 0,
            'products_with_predictions': 0
        }
        
        for product in products:
            # Delete old predictions
            db.query(Prediction).filter(
                Prediction.product_id == product.id,
                Prediction.target_date <= datetime.utcnow()
            ).delete()
            
            # Generate new predictions
            predictions = self.generate_predictions(db, product.id, days_ahead)
            
            if predictions:
                # Save predictions
                for pred in predictions:
                    db.add(pred)
                
                stats['predictions_generated'] += len(predictions)
                stats['products_with_predictions'] += 1
        
        db.commit()
        
        return stats
    
    def get_product_forecast(self, db: Session, product_id: int,
                           days_ahead: int = 30) -> List[Dict]:
        """
        Get forecast data for visualization
        
        Returns:
            List of dictionaries with date, predicted_demand, confidence
        """
        # Check if predictions exist
        existing_predictions = db.query(Prediction).filter(
            Prediction.product_id == product_id,
            Prediction.target_date >= datetime.utcnow()
        ).order_by(Prediction.target_date.asc()).limit(days_ahead).all()
        
        # If no predictions, generate them
        if not existing_predictions:
            predictions = self.generate_predictions(db, product_id, days_ahead)
            for pred in predictions:
                db.add(pred)
            db.commit()
        else:
            predictions = existing_predictions
        
        # Format for response
        forecast = []
        for pred in predictions:
            forecast.append({
                'date': pred.target_date.strftime('%Y-%m-%d'),
                'predicted_demand': pred.predicted_demand,
                'confidence_score': pred.confidence_score,
                'recommended_stock': pred.recommended_stock,
                'model_used': pred.model_used
            })
        
        return forecast
