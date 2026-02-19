"""
Machine Learning Model Training Module
Implements multiple algorithms for demand prediction
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
try:
    import tensorflow as tf
    import tf_keras as keras
    from tf_keras import layers
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("Warning: TensorFlow not available. LSTM model will be disabled.")
import joblib
import os
from datetime import datetime, timedelta
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')
from sklearn.ensemble import RandomForestRegressor

class DemandPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)



class DemandPredictor:
    """Demand prediction using multiple ML algorithms"""
    
    def __init__(self, model_path: str = "./models"):
        self.model_path = model_path
        os.makedirs(model_path, exist_ok=True)
        
        # Initialize models
        self.lr_model = None
        self.rf_model = None
        self.xgb_model = None
        self.lstm_model = None
        self.prophet_model = None
        
        # Model performance
        self.model_scores = {}
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features for training
        
        Args:
            df: DataFrame with columns: sale_date, quantity, product_id, unit_price
        
        Returns:
            X: Features DataFrame
            y: Target Series
        """
        df = df.copy()
        df['sale_date'] = pd.to_datetime(df['sale_date'])
        df = df.sort_values('sale_date')
        
        # Extract time-based features
        df['day_of_week'] = df['sale_date'].dt.dayofweek
        df['day_of_month'] = df['sale_date'].dt.day
        df['month'] = df['sale_date'].dt.month
        df['quarter'] = df['sale_date'].dt.quarter
        df['year'] = df['sale_date'].dt.year
        df['week_of_year'] = df['sale_date'].dt.isocalendar().week
        
        # Create lag features (previous sales)
        df['lag_1'] = df.groupby('product_id')['quantity'].shift(1)
        df['lag_7'] = df.groupby('product_id')['quantity'].shift(7)
        df['lag_30'] = df.groupby('product_id')['quantity'].shift(30)
        
        # Rolling statistics
        df['rolling_mean_7'] = df.groupby('product_id')['quantity'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        df['rolling_mean_30'] = df.groupby('product_id')['quantity'].transform(
            lambda x: x.rolling(window=30, min_periods=1).mean()
        )
        df['rolling_std_7'] = df.groupby('product_id')['quantity'].transform(
            lambda x: x.rolling(window=7, min_periods=1).std()
        )
        
        # Fill NaN values
        df = df.fillna(0)
        
        # Select features
        feature_columns = [
            'day_of_week', 'day_of_month', 'month', 'quarter', 'week_of_year',
            'lag_1', 'lag_7', 'lag_30',
            'rolling_mean_7', 'rolling_mean_30', 'rolling_std_7'
        ]
        
        X = df[feature_columns]
        y = df['quantity']
        
        return X, y
    
    def train_linear_regression(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Train Linear Regression model"""
        print("Training Linear Regression model...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.lr_model = LinearRegression()
        self.lr_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.lr_model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred, "Linear Regression")
        
        # Save model
        joblib.dump(self.lr_model, os.path.join(self.model_path, 'lr_model.pkl'))
        
        return metrics
    
    def train_random_forest(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Train Random Forest model"""
        print("Training Random Forest model...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.rf_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        self.rf_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.rf_model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred, "Random Forest")
        
        # Save model
        joblib.dump(self.rf_model, os.path.join(self.model_path, 'rf_model.pkl'))
        
        return metrics
    
    def train_xgboost(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Train XGBoost model"""
        print("Training XGBoost model...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            n_jobs=-1
        )
        self.xgb_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.xgb_model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred, "XGBoost")
        
        # Save model
        joblib.dump(self.xgb_model, os.path.join(self.model_path, 'xgb_model.pkl'))
        
        return metrics
    
    def train_lstm(self, X: pd.DataFrame, y: pd.Series, sequence_length: int = 30) -> Dict[str, float]:
        """Train LSTM neural network"""
        if not TF_AVAILABLE:
            print("Skipping LSTM training (TensorFlow not available)")
            return {}

        print("Training LSTM model...")
        
        # Prepare sequences for LSTM
        X_seq, y_seq = self._prepare_sequences(X.values, y.values, sequence_length)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_seq, y_seq, test_size=0.2, random_state=42
        )
        
        # Build LSTM model
        self.lstm_model = keras.Sequential([
            layers.LSTM(64, activation='relu', return_sequences=True, 
                       input_shape=(sequence_length, X.shape[1])),
            layers.Dropout(0.2),
            layers.LSTM(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1)
        ])
        
        self.lstm_model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        # Train with early stopping
        early_stop = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        self.lstm_model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            callbacks=[early_stop],
            verbose=0
        )
        
        # Evaluate
        y_pred = self.lstm_model.predict(X_test, verbose=0).flatten()
        metrics = self._calculate_metrics(y_test, y_pred, "LSTM")
        
        # Save model
        self.lstm_model.save(os.path.join(self.model_path, 'lstm_model.h5'))
        
        return metrics
        
    def train_prophet(self, df: pd.DataFrame) -> Dict[str, float]:
        """Train Facebook Prophet model"""
        print("Training Prophet model...")
        
        # Prophet expects ds (date) and y (value) columns
        prophet_df = df[['sale_date', 'quantity']].rename(
            columns={'sale_date': 'ds', 'quantity': 'y'}
        )
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds']).dt.tz_localize(None)
        
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05
        )
        model.fit(prophet_df)
        self.prophet_model = model
        
        # Evaluate on last 20%
        train_size = int(len(prophet_df) * 0.8)
        test_df = prophet_df.iloc[train_size:]
        
        forecast = model.predict(test_df[['ds']])
        y_pred = forecast['yhat'].values
        y_true = test_df['y'].values
        
        metrics = self._calculate_metrics(y_true, y_pred, "Prophet")
        
        # Save model
        joblib.dump(self.prophet_model, os.path.join(self.model_path, 'prophet_model.pkl'))
        
        return metrics
    
    def _prepare_sequences(self, X: np.ndarray, y: np.ndarray, 
                          sequence_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare sequences for LSTM"""
        X_seq, y_seq = [], []
        
        for i in range(len(X) - sequence_length):
            X_seq.append(X[i:i + sequence_length])
            y_seq.append(y[i + sequence_length])
        
        return np.array(X_seq), np.array(y_seq)
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, 
                          model_name: str) -> Dict[str, float]:
        """Calculate evaluation metrics"""
        # Ensure non-negative predictions
        y_pred = np.maximum(y_pred, 0)
        
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-10))) * 100
        
        metrics = {
            'model': model_name,
            'rmse': float(rmse),
            'mae': float(mae),
            'r2': float(r2),
            'mape': float(mape),
            'accuracy': float(max(0, min(100, 100 - mape)))
        }
        
        print(f"\n{model_name} Metrics:")
        print(f"  RMSE: {rmse:.2f}")
        print(f"  MAE: {mae:.2f}")
        print(f"  R²: {r2:.3f}")
        print(f"  MAPE: {mape:.2f}%")
        print(f"  Accuracy: {metrics['accuracy']:.2f}%")
        
        self.model_scores[model_name] = metrics
        
        return metrics
    
    def train_all_models(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Train all models and return performance metrics
        
        Args:
            df: Sales data DataFrame
        
        Returns:
            Dictionary with metrics for all models
        """
        print("="*50)
        print("Starting model training pipeline...")
        print("="*50)
        
        # Prepare features
        X, y = self.prepare_features(df)
        
        # Train all models
        all_metrics = {}
        
        try:
            all_metrics['linear_regression'] = self.train_linear_regression(X, y)
        except Exception as e:
            print(f"Error training Linear Regression: {e}")
        
        try:
            all_metrics['random_forest'] = self.train_random_forest(X, y)
        except Exception as e:
            print(f"Error training Random Forest: {e}")
        
        try:
            all_metrics['xgboost'] = self.train_xgboost(X, y)
        except Exception as e:
            print(f"Error training XGBoost: {e}")
        
        try:
            all_metrics['lstm'] = self.train_lstm(X, y)
        except Exception as e:
            print(f"Error training LSTM: {e}")

        try:
            all_metrics['prophet'] = self.train_prophet(df)
        except Exception as e:
            print(f"Error training Prophet: {e}")
        
        # Find best model
        best_model = max(all_metrics.items(), key=lambda x: x[1]['accuracy'])
        print("\n" + "="*50)
        print(f"Best Model: {best_model[0]} with {best_model[1]['accuracy']:.2f}% accuracy")
        print("="*50)
        
        # Save metrics
        metrics_file = os.path.join(self.model_path, 'model_metrics.pkl')
        joblib.dump(all_metrics, metrics_file)
        
        return all_metrics
    
    def load_models(self):
        """Load all trained models"""
        try:
            self.lr_model = joblib.load(os.path.join(self.model_path, 'lr_model.pkl'))
        except:
            print("Linear Regression model not found")
        
        try:
            self.rf_model = joblib.load(os.path.join(self.model_path, 'rf_model.pkl'))
        except:
            print("Random Forest model not found")
        
        try:
            self.xgb_model = joblib.load(os.path.join(self.model_path, 'xgb_model.pkl'))
        except:
            print("XGBoost model not found")
        
        if TF_AVAILABLE:
            try:
                self.lstm_model = keras.models.load_model(
                    os.path.join(self.model_path, 'lstm_model.h5')
                )
            except:
                print("LSTM model not found")
        else:
            print("Skipping LSTM model load (TensorFlow not available)")
    
    def predict_ensemble(self, X: pd.DataFrame) -> Tuple[float, float]:
        """
        Make ensemble prediction using all models
        
        Returns:
            prediction, confidence_score
        """
        predictions = []
        weights = []
        
        if self.lr_model:
            pred = self.lr_model.predict(X)[0]
            predictions.append(pred)
            weights.append(self.model_scores.get('Linear Regression', {}).get('accuracy', 50))
        
        if self.rf_model:
            pred = self.rf_model.predict(X)[0]
            predictions.append(pred)
            weights.append(self.model_scores.get('Random Forest', {}).get('accuracy', 50))
        
        if self.xgb_model:
            pred = self.xgb_model.predict(X)[0]
            predictions.append(pred)
            weights.append(self.model_scores.get('XGBoost', {}).get('accuracy', 50))
            
        if self.prophet_model:
            # Note: Prophet needs a dataframe with 'ds' column.
            # This logic assumes the 'X' features contain enough date info to reconstruct ds or we pass ds.
            # For simplicity in ensemble, we use it mainly in batch. 
            # In real-time, we might skip prophet if ds is not provided easily.
            pass
        
        if predictions:
            # Weighted average
            ensemble_pred = np.average(predictions, weights=weights)
            confidence = np.mean(weights)
            return float(max(0, ensemble_pred)), float(confidence)
        
        return 0.0, 0.0


# Example usage
if __name__ == "__main__":
    # Demo with sample data
    from sqlalchemy import create_engine
    from ...core.config import settings
    
    engine = create_engine(settings.DATABASE_URL)
    
    # Load sales data
    query = """
    SELECT s.sale_date, s.quantity, s.product_id, s.unit_price
    FROM sales s
    ORDER BY s.sale_date
    """
    
    df = pd.read_sql(query, engine)
    
    # Train models
    predictor = DemandPredictor()
    metrics = predictor.train_all_models(df)
    
    print("\nModel training complete!")
    print(f"Models saved to: {predictor.model_path}")
