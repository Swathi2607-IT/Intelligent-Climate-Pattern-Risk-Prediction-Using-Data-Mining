"""
NOAA Methane (CH4) Data Ingestion Module
Pulls atmospheric methane concentration data from NOAA
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


class NOAAMethaneIngestion:
    """
    Handles ingestion of NOAA methane (CH4) atmospheric concentration data.
    
    Data Source: https://gml.noaa.gov/ccgg/trends_ch4/
    """
    
    def __init__(self, output_dir: str = "../../data/raw"):
        """
        Initialize the NOAA Methane ingestion pipeline.
        
        Args:
            output_dir (str): Directory to save raw data
        """
        self.output_dir = output_dir
        self.base_url = "https://gml.noaa.gov/webdata/ccgg/trends/ch4/"
        self.endpoints = {
            "monthly_mean": "ch4_mm_gl.txt",
            "annual_mean": "ch4_annmean_gl.txt"
        }
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
    
    def fetch_methane_data(self, dataset: str = "annual_mean") -> Optional[pd.DataFrame]:
        """
        Fetch methane concentration data from NOAA.
        
        Args:
            dataset (str): Type of dataset ('monthly_mean', 'annual_mean')
        
        Returns:
            pd.DataFrame: Methane concentration data
        """
        try:
            if dataset not in self.endpoints:
                raise ValueError(f"Invalid dataset type. Choose from: {list(self.endpoints.keys())}")
            
            url = f"{self.base_url}{self.endpoints[dataset]}"
            logger.info(f"Fetching data from: {url}")
            
            # Fetch data
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse the text file (skip comment lines starting with #)
            lines = response.text.split('\n')
            data_lines = [line for line in lines if not line.startswith('#') and line.strip()]
            
            # Parse based on dataset type
            if dataset == "annual_mean":
                # Format: year, mean, unc
                data = []
                for line in data_lines:
                    parts = line.split()
                    if len(parts) >= 3:
                        try:
                            data.append({
                                'year': int(parts[0]),
                                'ch4_mean_ppb': float(parts[1]),
                                'ch4_uncertainty': float(parts[2])
                            })
                        except ValueError:
                            continue
                df = pd.DataFrame(data)
            
            elif dataset == "monthly_mean":
                # Format: year, month, decimal_date, average, trend, ndays
                data = []
                for line in data_lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            data.append({
                                'year': int(parts[0]),
                                'month': int(parts[1]),
                                'decimal_date': float(parts[2]),
                                'ch4_average_ppb': float(parts[3]),
                                'ch4_trend': float(parts[4])
                            })
                        except ValueError:
                            continue
                df = pd.DataFrame(data)
            
            logger.info(f"Successfully fetched {len(df)} records from NOAA Methane database")
            return df
            
        except requests.RequestException as e:
            logger.error(f"Error fetching NOAA Methane data: {e}")
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
        filename = f"noaa_methane_{dataset_name}_{timestamp}.csv"
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
            datasets = ["annual_mean"]
        
        results = {}
        
        for dataset in datasets:
            logger.info(f"Ingesting {dataset} dataset...")
            df = self.fetch_methane_data(dataset)
            
            if df is not None:
                filepath = self.save_raw_data(df, dataset)
                results[dataset] = filepath
            else:
                logger.warning(f"Failed to ingest {dataset}")
        
        return results


def main():
    """Main execution function."""
    ingestion = NOAAMethaneIngestion()
    
    # Ingest annual mean data
    results = ingestion.ingest(datasets=["annual_mean", "monthly_mean"])
    
    logger.info(f"Ingestion complete. Processed {len(results)} datasets.")
    for dataset, filepath in results.items():
        logger.info(f"  - {dataset}: {filepath}")


if __name__ == "__main__":
    main()
