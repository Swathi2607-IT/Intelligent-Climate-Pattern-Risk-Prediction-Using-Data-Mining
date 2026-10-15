"""
NASA GISS Temperature Data Ingestion Module
Pulls global temperature anomaly data from NASA GISS
"""

import requests
import pandas as pd
from typing import Optional, Dict
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NASAGISSIngestion:
    """
    Handles ingestion of NASA GISS temperature anomaly data.
    
    Data Source: https://data.giss.nasa.gov/gistemp/
    """
    
    def __init__(self, output_dir: str = "../../data/raw"):
        """
        Initialize the NASA GISS ingestion pipeline.
        
        Args:
            output_dir (str): Directory to save raw data
        """
        self.output_dir = output_dir
        self.base_url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/"
        self.endpoints = {
            "global_mean": "GLB.Ts+dSST.csv",
            "northern_hemisphere": "NH.Ts+dSST.csv",
            "southern_hemisphere": "SH.Ts+dSST.csv"
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def fetch_temperature_data(self, dataset: str = "global_mean") -> Optional[pd.DataFrame]:
        """
        Fetch temperature anomaly data from NASA GISS.
        
        Args:
            dataset (str): Type of dataset ('global_mean', 'northern_hemisphere', 'southern_hemisphere')
        
        Returns:
            pd.DataFrame: Temperature anomaly data
        """
        try:
            if dataset not in self.endpoints:
                raise ValueError(f"Invalid dataset type. Choose from: {list(self.endpoints.keys())}")
            
            url = f"{self.base_url}{self.endpoints[dataset]}"
            logger.info(f"Fetching data from: {url}")
            
            # Fetch data
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV data (skip first row which is metadata)
            from io import StringIO
            df = pd.read_csv(StringIO(response.text), skiprows=1)
            
            logger.info(f"Successfully fetched {len(df)} records from NASA GISS")
            return df
            
        except requests.RequestException as e:
            logger.error(f"Error fetching NASA GISS data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None
    
    def save_raw_data(self, df: pd.DataFrame, dataset_name: str) -> str:
        """
        Save raw data to local storage.
        
        Args:
            df (pd.DataFrame): Data to save
            dataset_name (str): Name of the dataset
        
        Returns:
            str: Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nasa_giss_{dataset_name}_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        df.to_csv(filepath, index=False)
        logger.info(f"Saved raw data to: {filepath}")
        
        return filepath
    
    def ingest(self, datasets: list = None) -> Dict[str, str]:
        """
        Main ingestion workflow.
        
        Args:
            datasets (list): List of dataset types to ingest
        
        Returns:
            Dict[str, str]: Dictionary mapping dataset names to file paths
        """
        if datasets is None:
            datasets = ["global_mean"]
        
        results = {}
        
        for dataset in datasets:
            logger.info(f"Ingesting {dataset} dataset...")
            df = self.fetch_temperature_data(dataset)
            
            if df is not None:
                filepath = self.save_raw_data(df, dataset)
                results[dataset] = filepath
            else:
                logger.warning(f"Failed to ingest {dataset}")
        
        return results


def main():
    """Main execution function."""
    ingestion = NASAGISSIngestion()
    
    # Ingest all available datasets
    results = ingestion.ingest(datasets=["global_mean", "northern_hemisphere", "southern_hemisphere"])
    
    logger.info(f"Ingestion complete. Processed {len(results)} datasets.")
    for dataset, filepath in results.items():
        logger.info(f"  - {dataset}: {filepath}")


if __name__ == "__main__":
    main()
