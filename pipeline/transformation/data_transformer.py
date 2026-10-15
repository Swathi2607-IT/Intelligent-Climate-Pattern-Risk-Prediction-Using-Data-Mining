"""
Data Cleaning and Transformation Module
Handles data cleaning, schema standardization, and feature engineering
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClimateDataTransformer:
    """
    Transforms raw climate data into clean, standardized format.
    """
    
    def __init__(self, input_dir: str = "../../data/raw", output_dir: str = "../../data/processed"):
        """
        Initialize the data transformer.
        
        Args:
            input_dir (str): Directory containing raw data
            output_dir (str): Directory to save processed data
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def clean_temperature_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean temperature anomaly data.
        
        Args:
            df (pd.DataFrame): Raw temperature data
        
        Returns:
            pd.DataFrame: Cleaned temperature data
        """
        logger.info("Cleaning temperature data...")
        
        # Create a copy
        df_clean = df.copy()
        
        # Handle missing values
        df_clean = df_clean.dropna(subset=['year'])
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates(subset=['year'], keep='last')
        
        # Ensure year is integer
        df_clean['year'] = df_clean['year'].astype(int)
        
        # Standardize column names
        if 'global_temp_anomaly' in df_clean.columns:
            df_clean = df_clean.rename(columns={'global_temp_anomaly': 'temp_anomaly_c'})
        
        # Remove outliers (values beyond 3 standard deviations)
        if 'temp_anomaly_c' in df_clean.columns:
            mean = df_clean['temp_anomaly_c'].mean()
            std = df_clean['temp_anomaly_c'].std()
            df_clean = df_clean[
                (df_clean['temp_anomaly_c'] >= mean - 3*std) & 
                (df_clean['temp_anomaly_c'] <= mean + 3*std)
            ]
        
        # Sort by year
        df_clean = df_clean.sort_values('year').reset_index(drop=True)
        
        logger.info(f"Temperature data cleaned: {len(df_clean)} records")
        return df_clean
    
    def clean_co2_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean CO2 concentration data.
        
        Args:
            df (pd.DataFrame): Raw CO2 data
        
        Returns:
            pd.DataFrame: Cleaned CO2 data
        """
        logger.info("Cleaning CO2 data...")
        
        df_clean = df.copy()
        
        # Handle missing values
        df_clean = df_clean.dropna(subset=['year'])
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates(subset=['year'], keep='last')
        
        # Ensure year is integer
        df_clean['year'] = df_clean['year'].astype(int)
        
        # Standardize column names
        if 'co2_ppm' not in df_clean.columns:
            if 'co2_mean' in df_clean.columns:
                df_clean = df_clean.rename(columns={'co2_mean': 'co2_ppm'})
            elif 'co2_average' in df_clean.columns:
                df_clean = df_clean.rename(columns={'co2_average': 'co2_ppm'})
        
        # Remove invalid values (CO2 should be positive and within reasonable range)
        if 'co2_ppm' in df_clean.columns:
            df_clean = df_clean[
                (df_clean['co2_ppm'] > 200) & 
                (df_clean['co2_ppm'] < 600)
            ]
        
        # Sort by year
        df_clean = df_clean.sort_values('year').reset_index(drop=True)
        
        logger.info(f"CO2 data cleaned: {len(df_clean)} records")
        return df_clean
    
    def clean_methane_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean methane concentration data.
        
        Args:
            df (pd.DataFrame): Raw methane data
        
        Returns:
            pd.DataFrame: Cleaned methane data
        """
        logger.info("Cleaning methane data...")
        
        df_clean = df.copy()
        
        # Handle missing values
        df_clean = df_clean.dropna(subset=['year'])
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates(subset=['year'], keep='last')
        
        # Ensure year is integer
        df_clean['year'] = df_clean['year'].astype(int)
        
        # Standardize column names
        if 'methane_ppb' not in df_clean.columns:
            if 'ch4_mean_ppb' in df_clean.columns:
                df_clean = df_clean.rename(columns={'ch4_mean_ppb': 'methane_ppb'})
            elif 'ch4_average_ppb' in df_clean.columns:
                df_clean = df_clean.rename(columns={'ch4_average_ppb': 'methane_ppb'})
        
        # Remove invalid values (methane should be positive and within reasonable range)
        if 'methane_ppb' in df_clean.columns:
            df_clean = df_clean[
                (df_clean['methane_ppb'] > 500) & 
                (df_clean['methane_ppb'] < 3000)
            ]
        
        # Sort by year
        df_clean = df_clean.sort_values('year').reset_index(drop=True)
        
        logger.info(f"Methane data cleaned: {len(df_clean)} records")
        return df_clean
    
    def clean_sealevel_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean sea level rise data.
        
        Args:
            df (pd.DataFrame): Raw sea level data
        
        Returns:
            pd.DataFrame: Cleaned sea level data
        """
        logger.info("Cleaning sea level data...")
        
        df_clean = df.copy()
        
        # Handle missing values
        df_clean = df_clean.dropna(subset=['year'])
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates(subset=['year'], keep='last')
        
        # Ensure year is integer
        df_clean['year'] = df_clean['year'].astype(int)
        
        # Standardize column names
        if 'sea_level_mm' not in df_clean.columns:
            if 'GMSL' in df_clean.columns:
                df_clean = df_clean.rename(columns={'GMSL': 'sea_level_mm'})
        
        # Sort by year
        df_clean = df_clean.sort_values('year').reset_index(drop=True)
        
        logger.info(f"Sea level data cleaned: {len(df_clean)} records")
        return df_clean
    
    def merge_datasets(
        self, 
        temp_df: pd.DataFrame, 
        co2_df: pd.DataFrame, 
        methane_df: pd.DataFrame, 
        sealevel_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Merge all datasets by year.
        
        Args:
            temp_df (pd.DataFrame): Temperature data
            co2_df (pd.DataFrame): CO2 data
            methane_df (pd.DataFrame): Methane data
            sealevel_df (pd.DataFrame): Sea level data
        
        Returns:
            pd.DataFrame: Merged dataset
        """
        logger.info("Merging datasets...")
        
        # Start with temperature data
        merged = temp_df[['year', 'temp_anomaly_c']].copy()
        
        # Merge CO2 data
        if 'co2_ppm' in co2_df.columns:
            merged = merged.merge(
                co2_df[['year', 'co2_ppm']], 
                on='year', 
                how='outer'
            )
        
        # Merge methane data
        if 'methane_ppb' in methane_df.columns:
            merged = merged.merge(
                methane_df[['year', 'methane_ppb']], 
                on='year', 
                how='outer'
            )
        
        # Merge sea level data
        if 'sea_level_mm' in sealevel_df.columns:
            merged = merged.merge(
                sealevel_df[['year', 'sea_level_mm']], 
                on='year', 
                how='outer'
            )
        
        # Sort by year
        merged = merged.sort_values('year').reset_index(drop=True)
        
        # Interpolate missing values
        merged = merged.interpolate(method='linear', limit_direction='both')
        
        logger.info(f"Merged dataset created: {len(merged)} records, {len(merged.columns)} columns")
        return merged
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create derived features from raw data.
        
        Args:
            df (pd.DataFrame): Merged clean data
        
        Returns:
            pd.DataFrame: Data with engineered features
        """
        logger.info("Engineering features...")
        
        df_features = df.copy()
        
        # Decade feature
        df_features['decade'] = (df_features['year'] // 10) * 10
        
        # Moving averages (5-year and 10-year)
        if 'temp_anomaly_c' in df_features.columns:
            df_features['temp_ma_5yr'] = df_features['temp_anomaly_c'].rolling(window=5, center=True).mean()
            df_features['temp_ma_10yr'] = df_features['temp_anomaly_c'].rolling(window=10, center=True).mean()
        
        if 'co2_ppm' in df_features.columns:
            df_features['co2_ma_5yr'] = df_features['co2_ppm'].rolling(window=5, center=True).mean()
            df_features['co2_growth_rate'] = df_features['co2_ppm'].diff()
        
        if 'methane_ppb' in df_features.columns:
            df_features['methane_ma_5yr'] = df_features['methane_ppb'].rolling(window=5, center=True).mean()
            df_features['methane_growth_rate'] = df_features['methane_ppb'].diff()
        
        if 'sea_level_mm' in df_features.columns:
            df_features['sea_level_rate'] = df_features['sea_level_mm'].diff()
        
        # Standardized/normalized values
        for col in ['temp_anomaly_c', 'co2_ppm', 'methane_ppb', 'sea_level_mm']:
            if col in df_features.columns:
                df_features[f'{col}_normalized'] = (
                    (df_features[col] - df_features[col].mean()) / df_features[col].std()
                )
        
        logger.info(f"Feature engineering complete: {len(df_features.columns)} features")
        return df_features
    
    def detect_outliers(self, df: pd.DataFrame, column: str) -> pd.Series:
        """
        Detect outliers using IQR method.
        
        Args:
            df (pd.DataFrame): Data
            column (str): Column to check for outliers
        
        Returns:
            pd.Series: Boolean series indicating outliers
        """
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
        
        logger.info(f"Detected {outliers.sum()} outliers in {column}")
        return outliers
    
    def save_processed_data(self, df: pd.DataFrame, filename: str) -> str:
        """
        Save processed data to file.
        
        Args:
            df (pd.DataFrame): Processed data
            filename (str): Output filename
        
        Returns:
            str: Path to saved file
        """
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        logger.info(f"Saved processed data to: {filepath}")
        return filepath
    
    def transform(self, sample_data_path: str = None) -> str:
        """
        Main transformation workflow.
        
        Args:
            sample_data_path (str): Path to sample data file
        
        Returns:
            str: Path to processed data file
        """
        if sample_data_path is None:
            sample_data_path = "../../data/sample/climate_sample.csv"
        
        # Load sample data
        logger.info(f"Loading data from: {sample_data_path}")
        df = pd.read_csv(sample_data_path)
        
        # Clean each component
        temp_df = self.clean_temperature_data(df[['year', 'global_temp_anomaly']])
        co2_df = self.clean_co2_data(df[['year', 'co2_ppm']])
        methane_df = self.clean_methane_data(df[['year', 'methane_ppb']])
        sealevel_df = self.clean_sealevel_data(df[['year', 'sea_level_mm']])
        
        # Merge datasets
        merged_df = self.merge_datasets(temp_df, co2_df, methane_df, sealevel_df)
        
        # Engineer features
        final_df = self.engineer_features(merged_df)
        
        # Save processed data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.save_processed_data(final_df, f"climate_processed_{timestamp}.csv")
        
        # Also save a static version for easy access
        self.save_processed_data(final_df, "climate_processed_latest.csv")
        
        logger.info("Transformation complete!")
        return output_file


def main():
    """Main execution function."""
    # Use absolute path
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sample_data_path = os.path.join(base_dir, "data", "sample", "climate_sample.csv")
    
    transformer = ClimateDataTransformer()
    output_file = transformer.transform(sample_data_path=sample_data_path)
    logger.info(f"Processed data saved to: {output_file}")


if __name__ == "__main__":
    main()
