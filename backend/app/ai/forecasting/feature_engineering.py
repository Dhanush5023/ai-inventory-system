import pandas as pd
import numpy as np
from typing import Dict, List


class FeatureEngine:
    """Advanced feature engineering for demand forecasting"""

    @staticmethod
    def detect_seasonality(
        df: pd.DataFrame,
        value_column: str = 'quantity',
        periods: List[int] = [7, 30, 365]
    ) -> Dict[int, float]:
        """
        Detect seasonality in time series data using autocorrelation
        """
        from scipy import signal

        if len(df) < max(periods):
            return {period: 0.0 for period in periods}

        values = df[value_column].values
        seasonality_scores = {}

        for period in periods:
            if len(values) < period * 2:
                seasonality_scores[period] = 0.0
                continue

            # Calculate autocorrelation at lag=period
            autocorr = np.corrcoef(values[:-period], values[period:])[0, 1]
            seasonality_scores[period] = abs(autocorr) if not np.isnan(autocorr) else 0.0

        return seasonality_scores

    @staticmethod
    def add_seasonal_indices(
        df: pd.DataFrame,
        date_column: str = 'date'
    ) -> pd.DataFrame:
        """Add cyclical encoding for seasonal patterns"""
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])

        # Day of year (yearly seasonality)
        day_of_year = df[date_column].dt.dayofyear
        df['day_of_year_sin'] = np.sin(2 * np.pi * day_of_year / 365.25)
        df['day_of_year_cos'] = np.cos(2 * np.pi * day_of_year / 365.25)

        # Day of week (weekly seasonality)
        day_of_week = df[date_column].dt.dayofweek
        df['day_of_week_sin'] = np.sin(2 * np.pi * day_of_week / 7)
        df['day_of_week_cos'] = np.cos(2 * np.pi * day_of_week / 7)

        # Day of month (monthly seasonality)
        day_of_month = df[date_column].dt.day
        df['day_of_month_sin'] = np.sin(2 * np.pi * day_of_month / 30)
        df['day_of_month_cos'] = np.cos(2 * np.pi * day_of_month / 30)

        return df

    @staticmethod
    def add_holiday_features(
        df: pd.DataFrame,
        date_column: str = 'date'
    ) -> pd.DataFrame:
        """Add boolean features for major sales periods/holidays"""
        df = df.copy()
        dates = pd.to_datetime(df[date_column])
        
        # Binary flags for major shopping periods
        # Black Friday / Cyber Monday (late Nov)
        df['is_shopping_season'] = ((dates.dt.month == 11) & (dates.dt.day >= 20)) | \
                                   ((dates.dt.month == 12) & (dates.dt.day <= 24))
        
        # Specific holidays
        df['is_year_end'] = (dates.dt.month == 12) & (dates.dt.day >= 25)
        
        # Day of week preference (e.g. weekends have higher sales)
        df['is_weekend'] = dates.dt.dayofweek >= 5
        
        return df

    @staticmethod
    def add_trend_features(
        df: pd.DataFrame,
        value_column: str = 'quantity'
    ) -> pd.DataFrame:
        """Add trend-based features"""
        df = df.copy()

        # Simple linear trend
        df['trend'] = np.arange(len(df))

        # Change from previous period
        df['pct_change'] = df[value_column].pct_change().fillna(0)

        # Exponential moving average
        df['ema_7'] = df[value_column].ewm(span=7, adjust=False).mean()
        df['ema_30'] = df[value_column].ewm(span=30, adjust=False).mean()

        return df

    @staticmethod
    def add_volatility_features(
        df: pd.DataFrame,
        value_column: str = 'quantity',
        windows: List[int] = [7, 14, 30]
    ) -> pd.DataFrame:
        """Add volatility/variance features"""
        df = df.copy()

        for window in windows:
            # Coefficient of variation
            rolling_mean = df[value_column].rolling(window=window, min_periods=1).mean()
            rolling_std = df[value_column].rolling(window=window, min_periods=1).std()

            df[f'cv_{window}'] = (rolling_std / rolling_mean).replace([np.inf, -np.inf], 0).fillna(0)

        return df

    @staticmethod
    def create_fourier_features(
        df: pd.DataFrame,
        date_column: str = 'date',
        n_components: int = 5,
        period: int = 365
    ) -> pd.DataFrame:
        """Create Fourier features for capturing complex seasonality"""
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])

        # Time index
        t = (df[date_column] - df[date_column].min()).dt.days

        for k in range(1, n_components + 1):
            df[f'fourier_sin_{k}'] = np.sin(2 * np.pi * k * t / period)
            df[f'fourier_cos_{k}'] = np.cos(2 * np.pi * k * t / period)

        return df

    @staticmethod
    def engineer_all_features(
        df: pd.DataFrame,
        date_column: str = 'date',
        value_column: str = 'quantity'
    ) -> pd.DataFrame:
        """Apply all feature engineering techniques"""
        df = df.copy()

        # Add seasonal indices
        df = FeatureEngine.add_seasonal_indices(df, date_column)

        # Add trend features
        df = FeatureEngine.add_trend_features(df, value_column)

        # Add Volatility features
        df = FeatureEngine.add_volatility_features(df, value_column)

        # Add Holiday features
        df = FeatureEngine.add_holiday_features(df, date_column)

        # Add Fourier features
        df = FeatureEngine.create_fourier_features(df, date_column)

        return df
