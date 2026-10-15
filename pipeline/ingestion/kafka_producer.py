"""
Kafka Producer for Climate Data Streaming
Simulates real-time climate data ingestion via Kafka
"""

from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClimateDataProducer:
    """
    Kafka producer for streaming climate data.
    """
    
    def __init__(self, bootstrap_servers: list = ['localhost:9092']):
        """
        Initialize Kafka producer.
        
        Args:
            bootstrap_servers (list): List of Kafka broker addresses
        """
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.topics = {
            'temperature': 'climate.temperature',
            'co2': 'climate.co2',
            'methane': 'climate.methane',
            'sea_level': 'climate.sealevel'
        }
    
    def connect(self):
        """Establish connection to Kafka broker."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Connected to Kafka brokers: {self.bootstrap_servers}")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def send_message(self, topic: str, data: Dict[str, Any], key: str = None):
        """
        Send a message to Kafka topic.
        
        Args:
            topic (str): Kafka topic name
            data (Dict): Data to send
            key (str): Message key for partitioning
        """
        try:
            # Add timestamp to data
            data['timestamp'] = datetime.now().isoformat()
            
            # Send message
            future = self.producer.send(topic, value=data, key=key)
            
            # Wait for acknowledgment
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                f"Message sent to {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
            
        except KafkaError as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    def stream_temperature_data(self, df: pd.DataFrame):
        """
        Stream temperature data to Kafka.
        
        Args:
            df (pd.DataFrame): Temperature data
        """
        topic = self.topics['temperature']
        logger.info(f"Streaming temperature data to {topic}")
        
        for _, row in df.iterrows():
            data = {
                'year': int(row.get('year', 0)),
                'temperature_anomaly': float(row.get('global_temp_anomaly', 0)),
                'source': 'NASA_GISS'
            }
            self.send_message(topic, data, key=str(data['year']))
            time.sleep(0.1)  # Simulate real-time streaming
    
    def stream_co2_data(self, df: pd.DataFrame):
        """
        Stream CO2 data to Kafka.
        
        Args:
            df (pd.DataFrame): CO2 data
        """
        topic = self.topics['co2']
        logger.info(f"Streaming CO2 data to {topic}")
        
        for _, row in df.iterrows():
            data = {
                'year': int(row.get('year', 0)),
                'co2_ppm': float(row.get('co2_ppm', 0)),
                'source': 'NOAA'
            }
            self.send_message(topic, data, key=str(data['year']))
            time.sleep(0.1)
    
    def stream_methane_data(self, df: pd.DataFrame):
        """
        Stream methane data to Kafka.
        
        Args:
            df (pd.DataFrame): Methane data
        """
        topic = self.topics['methane']
        logger.info(f"Streaming methane data to {topic}")
        
        for _, row in df.iterrows():
            data = {
                'year': int(row.get('year', 0)),
                'methane_ppb': float(row.get('methane_ppb', 0)),
                'source': 'NOAA'
            }
            self.send_message(topic, data, key=str(data['year']))
            time.sleep(0.1)
    
    def stream_sealevel_data(self, df: pd.DataFrame):
        """
        Stream sea level data to Kafka.
        
        Args:
            df (pd.DataFrame): Sea level data
        """
        topic = self.topics['sea_level']
        logger.info(f"Streaming sea level data to {topic}")
        
        for _, row in df.iterrows():
            data = {
                'year': int(row.get('year', 0)),
                'sea_level_mm': float(row.get('sea_level_mm', 0)),
                'source': 'NOAA'
            }
            self.send_message(topic, data, key=str(data['year']))
            time.sleep(0.1)
    
    def close(self):
        """Close Kafka producer connection."""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed")


def main():
    """Main execution function."""
    # Load sample data
    sample_data_path = "../../data/sample/climate_sample.csv"
    df = pd.read_csv(sample_data_path)
    
    # Initialize producer
    producer = ClimateDataProducer()
    
    try:
        producer.connect()
        
        # Stream all data types
        producer.stream_temperature_data(df[['year', 'global_temp_anomaly']])
        producer.stream_co2_data(df[['year', 'co2_ppm']])
        producer.stream_methane_data(df[['year', 'methane_ppb']])
        producer.stream_sealevel_data(df[['year', 'sea_level_mm']])
        
        logger.info("All data streamed successfully")
        
    except Exception as e:
        logger.error(f"Error during streaming: {e}")
    finally:
        producer.close()


if __name__ == "__main__":
    main()
