"""
Machine Learning Models for Climate Data Analysis
Includes trend estimation, time-series forecasting, and correlation analysis
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import logging
from typing import Dict, Tuple, Any
import os
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """
    Analyzes trends in climate data using various methods.
    """
    
    def __init__(self, model_dir: str = "./models"):
        """
        Initialize trend analyzer.
        
        Args:
            model_dir (str): Directory to save models
        """
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.models = {}
    
    def linear_trend(self, df: pd.DataFrame, feature: str) -> Dict[str, Any]:
        """
        Calculate linear trend for a feature.
        
        Args:
            df (pd.DataFrame): Climate data
            feature (str): Feature to analyze
        
        Returns:
            Dict: Trend analysis results
        """
        logger.info(f"Analyzing linear trend for {feature}")
        
        # Prepare data
        X = df[['year']].values
        y = df[feature].values
        
        # Remove NaN values
        mask = ~np.isnan(y)
        X = X[mask]
        y = y[mask]
        
        # Fit linear regression
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate predictions
        y_pred = model.predict(X)
        
        # Calculate metrics
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        # Calculate trend (slope)
        slope = model.coef_[0]
        intercept = model.intercept_
        
        # Save model
        model_path = os.path.join(self.model_dir, f"linear_trend_{feature}.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        results = {
            'feature': feature,
            'slope': slope,
            'intercept': intercept,
            'r2_score': r2,
            'rmse': rmse,
            'model_path': model_path,
            'trend_direction': 'increasing' if slope > 0 else 'decreasing',
            'annual_change': slope
        }
        
        logger.info(f"Linear trend: slope={slope:.6f}, R²={r2:.4f}")
        
        return results
    
    def moving_average_trend(self, df: pd.DataFrame, feature: str, window: int = 10) -> pd.DataFrame:
        """
        Calculate moving average trend.
        
        Args:
            df (pd.DataFrame): Climate data
            feature (str): Feature to analyze
            window (int): Window size for moving average
        
        Returns:
            pd.DataFrame: Data with moving average column
        """
        logger.info(f"Calculating {window}-year moving average for {feature}")
        
        df_trend = df.copy()
        df_trend[f'{feature}_ma_{window}y'] = df_trend[feature].rolling(window=window, center=True).mean()
        
        return df_trend
    
    def exponential_smoothing_trend(self, series: pd.Series, alpha: float = 0.3) -> pd.Series:
        """
        Apply exponential smoothing.
        
        Args:
            series (pd.Series): Time series data
            alpha (float): Smoothing parameter
        
        Returns:
            pd.Series: Smoothed series
        """
        logger.info(f"Applying exponential smoothing with alpha={alpha}")
        
        smoothed = series.ewm(alpha=alpha, adjust=False).mean()
        return smoothed


class TimeSeriesForecaster:
    """
    Forecasts future climate conditions using time-series models.
    """
    
    def __init__(self, model_dir: str = "./models"):
        """
        Initialize time-series forecaster.
        
        Args:
            model_dir (str): Directory to save models
        """
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
    
    def forecast_linear(self, df: pd.DataFrame, feature: str, years_ahead: int = 10) -> pd.DataFrame:
        """
        Forecast using linear regression.
        
        Args:
            df (pd.DataFrame): Historical climate data
            feature (str): Feature to forecast
            years_ahead (int): Number of years to forecast
        
        Returns:
            pd.DataFrame: Forecast data
        """
        logger.info(f"Forecasting {feature} for {years_ahead} years using linear regression")
        
        # Prepare historical data
        X_train = df[['year']].values
        y_train = df[feature].values
        
        # Remove NaN values
        mask = ~np.isnan(y_train)
        X_train = X_train[mask]
        y_train = y_train[mask]
        
        # Fit model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Generate future years
        last_year = int(df['year'].max())
        future_years = np.arange(last_year + 1, last_year + years_ahead + 1).reshape(-1, 1)
        
        # Make predictions
        predictions = model.predict(future_years)
        
        # Create forecast dataframe
        forecast_df = pd.DataFrame({
            'year': future_years.flatten(),
            f'{feature}_forecast': predictions,
            'forecast_method': 'linear_regression'
        })
        
        # Save model
        model_path = os.path.join(self.model_dir, f"forecast_{feature}_linear.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Forecast complete: {len(forecast_df)} predictions")
        
        return forecast_df
    
    def forecast_arima_simple(self, df: pd.DataFrame, feature: str, years_ahead: int = 10) -> pd.DataFrame:
        """
        Simple ARIMA-style forecast using statsmodels.
        
        Args:
            df (pd.DataFrame): Historical climate data
            feature (str): Feature to forecast
            years_ahead (int): Number of years to forecast
        
        Returns:
            pd.DataFrame: Forecast data
        """
        try:
            from statsmodels.tsa.arima.model import ARIMA
            
            logger.info(f"Forecasting {feature} for {years_ahead} years using ARIMA")
            
            # Prepare data
            series = df.set_index('year')[feature].dropna()
            
            # Fit ARIMA model (1,1,1) as default
            model = ARIMA(series, order=(1, 1, 1))
            model_fit = model.fit()
            
            # Make forecast
            forecast = model_fit.forecast(steps=years_ahead)
            
            # Create forecast dataframe
            last_year = int(df['year'].max())
            future_years = np.arange(last_year + 1, last_year + years_ahead + 1)
            
            forecast_df = pd.DataFrame({
                'year': future_years,
                f'{feature}_forecast': forecast.values,
                'forecast_method': 'ARIMA(1,1,1)'
            })
            
            # Save model
            model_path = os.path.join(self.model_dir, f"forecast_{feature}_arima.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model_fit, f)
            
            logger.info(f"ARIMA forecast complete: {len(forecast_df)} predictions")
            
            return forecast_df
            
        except ImportError:
            logger.warning("statsmodels not available, falling back to linear forecast")
            return self.forecast_linear(df, feature, years_ahead)
        except Exception as e:
            logger.error(f"ARIMA forecast failed: {e}, falling back to linear")
            return self.forecast_linear(df, feature, years_ahead)


class CorrelationAnalyzer:
    """
    Analyzes correlations between climate variables.
    """
    
    def __init__(self, model_dir: str = "./models"):
        """
        Initialize correlation analyzer.
        
        Args:
            model_dir (str): Directory to save models
        """
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
    
    def calculate_correlations(self, df: pd.DataFrame, features: list) -> pd.DataFrame:
        """
        Calculate correlation matrix.
        
        Args:
            df (pd.DataFrame): Climate data
            features (list): List of features to analyze
        
        Returns:
            pd.DataFrame: Correlation matrix
        """
        logger.info(f"Calculating correlations for {len(features)} features")
        
        # Select features and drop NaN
        df_corr = df[features].dropna()
        
        # Calculate Pearson correlation
        corr_matrix = df_corr.corr()
        
        logger.info("Correlation matrix calculated")
        
        return corr_matrix
    
    def co2_temperature_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Build regression model for CO2 vs Temperature relationship.
        
        Args:
            df (pd.DataFrame): Climate data
        
        Returns:
            Dict: Model results
        """
        logger.info("Building CO2 vs Temperature correlation model")
        
        # Prepare data
        data = df[['co2_ppm', 'temp_anomaly_c']].dropna()
        
        X = data[['co2_ppm']].values
        y = data['temp_anomaly_c'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Fit model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Metrics
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
        mae_test = mean_absolute_error(y_test, y_pred_test)
        
        # Save model
        model_path = os.path.join(self.model_dir, "co2_temperature_model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        results = {
            'model_type': 'CO2 vs Temperature',
            'coefficient': model.coef_[0],
            'intercept': model.intercept_,
            'r2_train': r2_train,
            'r2_test': r2_test,
            'rmse': rmse_test,
            'mae': mae_test,
            'model_path': model_path
        }
        
        logger.info(f"CO2-Temperature model: R²={r2_test:.4f}, RMSE={rmse_test:.4f}")
        
        return results
    
    def multivariate_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Build multivariate model with all features.
        
        Args:
            df (pd.DataFrame): Climate data
        
        Returns:
            Dict: Model results
        """
        logger.info("Building multivariate climate model")
        
        # Select features
        features = ['co2_ppm', 'methane_ppb', 'sea_level_mm']
        target = 'temp_anomaly_c'
        
        # Prepare data
        data = df[features + [target]].dropna()
        
        X = data[features].values
        y = data[target].values
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Fit model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Predictions
        y_pred_test = model.predict(X_test)
        
        # Metrics
        r2 = r2_score(y_test, y_pred_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
        mae = mean_absolute_error(y_test, y_pred_test)
        
        # Feature importance (coefficients)
        feature_importance = dict(zip(features, model.coef_))
        
        # Save model and scaler
        model_path = os.path.join(self.model_dir, "multivariate_climate_model.pkl")
        scaler_path = os.path.join(self.model_dir, "multivariate_scaler.pkl")
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        results = {
            'model_type': 'Multivariate Climate Model',
            'features': features,
            'target': target,
            'feature_importance': feature_importance,
            'r2_score': r2,
            'rmse': rmse,
            'mae': mae,
            'model_path': model_path,
            'scaler_path': scaler_path
        }
        
        logger.info(f"Multivariate model: R²={r2:.4f}, RMSE={rmse:.4f}")
        
        return results


def main():
    """Main execution function."""
    # Load processed data
    data_path = "../../data/processed/climate_processed_latest.csv"
    
    if not os.path.exists(data_path):
        data_path = "../../data/sample/climate_sample.csv"
    
    logger.info(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    
    # Initialize analyzers
    trend_analyzer = TrendAnalyzer(model_dir="../../pipeline/ml/models")
    forecaster = TimeSeriesForecaster(model_dir="../../pipeline/ml/models")
    corr_analyzer = CorrelationAnalyzer(model_dir="../../pipeline/ml/models")
    
    # Analyze trends
    logger.info("\n=== TREND ANALYSIS ===")
    temp_trend = trend_analyzer.linear_trend(df, 'temp_anomaly_c' if 'temp_anomaly_c' in df.columns else 'global_temp_anomaly')
    co2_trend = trend_analyzer.linear_trend(df, 'co2_ppm')
    
    # Forecast future values
    logger.info("\n=== FORECASTING ===")
    feature_col = 'temp_anomaly_c' if 'temp_anomaly_c' in df.columns else 'global_temp_anomaly'
    temp_forecast = forecaster.forecast_linear(df, feature_col, years_ahead=10)
    
    # Correlation analysis
    logger.info("\n=== CORRELATION ANALYSIS ===")
    features = ['co2_ppm', 'methane_ppb', 'sea_level_mm']
    if 'temp_anomaly_c' in df.columns:
        features.append('temp_anomaly_c')
    elif 'global_temp_anomaly' in df.columns:
        features.append('global_temp_anomaly')
    
    available_features = [f for f in features if f in df.columns]
    corr_matrix = corr_analyzer.calculate_correlations(df, available_features)
    
    logger.info("\n=== ML MODELING COMPLETE ===")
    logger.info(f"Models saved to: {trend_analyzer.model_dir}")


if __name__ == "__main__":
    main()
