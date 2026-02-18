import pandas as pd
import numpy as np
from typing import Tuple
from datetime import datetime
from sklearn.preprocessing import StandardScaler


class DataPreprocessor:
    """Preprocess sales data for ML models"""

    def __init__(self):
        self.scaler = StandardScaler()

    def create_time_series(
        self,
        df: pd.DataFrame,
        date_column: str = 'date',
        value_column: str = 'quantity'
    ) -> pd.DataFrame:
        """
        Create a complete time series with missing dates filled
        """
        if df.empty:
            return df

        # Ensure date column is datetime
        df[date_column] = pd.to_datetime(df[date_column])

        # Create complete date range
        date_range = pd.date_range(
            start=df[date_column].min(),
            end=df[date_column].max(),
            freq='D'
        )

        # Create complete dataframe
        complete_df = pd.DataFrame({date_column: date_range})

        # Merge with original data
        result = complete_df.merge(df, on=date_column, how='left')

        # Fill missing values with 0 (no sales on that day)
        result[value_column] = result[value_column].fillna(0)

        return result

    def add_time_features(self, df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
        """Add time-based features"""
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])

        # Extract time components
        df['day_of_week'] = df[date_column].dt.dayofweek
        df['day_of_month'] = df[date_column].dt.day
        df['week_of_year'] = df[date_column].dt.isocalendar().week
        df['month'] = df[date_column].dt.month
        df['quarter'] = df[date_column].dt.quarter
        df['year'] = df[date_column].dt.year

        # Is weekend
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

        # Month start/end
        df['is_month_start'] = df[date_column].dt.is_month_start.astype(int)
        df['is_month_end'] = df[date_column].dt.is_month_end.astype(int)

        return df

    def add_lag_features(
        self,
        df: pd.DataFrame,
        value_column: str = 'quantity',
        lags: list = [1, 7, 14, 30]
    ) -> pd.DataFrame:
        """Add lag features"""
        df = df.copy()

        for lag in lags:
            df[f'{value_column}_lag_{lag}'] = df[value_column].shift(lag)

        return df

    def add_rolling_features(
        self,
        df: pd.DataFrame,
        value_column: str = 'quantity',
        windows: list = [7, 14, 30]
    ) -> pd.DataFrame:
        """Add rolling window statistics"""
        df = df.copy()

        for window in windows:
            df[f'{value_column}_rolling_mean_{window}'] = (
                df[value_column].rolling(window=window, min_periods=1).mean()
            )
            df[f'{value_column}_rolling_std_{window}'] = (
                df[value_column].rolling(window=window, min_periods=1).std()
            )
            df[f'{value_column}_rolling_max_{window}'] = (
                df[value_column].rolling(window=window, min_periods=1).max()
            )
            df[f'{value_column}_rolling_min_{window}'] = (
                df[value_column].rolling(window=window, min_periods=1).min()
            )

        return df

    def prepare_features(
        self,
        df: pd.DataFrame,
        date_column: str = 'date',
        value_column: str = 'quantity'
    ) -> pd.DataFrame:
        """Complete feature engineering pipeline"""
        # Create complete time series
        df = self.create_time_series(df, date_column, value_column)

        # Add time features
        df = self.add_time_features(df, date_column)

        # Add lag features
        df = self.add_lag_features(df, value_column)

        # Add rolling features
        df = self.add_rolling_features(df, value_column)

        # Drop rows with NaN (from lag features)
        df = df.dropna()

        return df

    def scale_features(
        self,
        X: np.ndarray,
        fit: bool = True
    ) -> np.ndarray:
        """Scale features using StandardScaler"""
        if fit:
            return self.scaler.fit_transform(X)
        else:
            return self.scaler.transform(X)

    def train_test_split(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split time series data chronologically"""
        split_idx = int(len(df) * (1 - test_size))
        train = df.iloc[:split_idx]
        test = df.iloc[split_idx:]
        return train, test
