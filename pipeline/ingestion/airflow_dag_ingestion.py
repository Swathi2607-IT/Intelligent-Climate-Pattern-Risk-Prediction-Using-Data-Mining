"""
Airflow DAG for Climate Data Ingestion Pipeline
Orchestrates data ingestion from multiple sources
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import logging

# Import custom ingestion modules
import sys
sys.path.append('/opt/airflow/dags')

from nasa_giss_ingestion import NASAGISSIngestion
from noaa_co2_ingestion import NOAACO2Ingestion
from noaa_methane_ingestion import NOAAMethaneIngestion
from noaa_sealevel_ingestion import NOAASeaLevelIngestion

logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'climate_team',
    'depends_on_past': False,
    'email': ['climate-alerts@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1),
}

# Define the DAG
dag = DAG(
    'climate_data_ingestion',
    default_args=default_args,
    description='Daily ingestion of climate data from NASA and NOAA',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['climate', 'ingestion', 'etl'],
)


def ingest_nasa_temperature(**context):
    """Task to ingest NASA GISS temperature data."""
    logger.info("Starting NASA GISS temperature data ingestion")
    
    ingestion = NASAGISSIngestion(output_dir='/data/raw')
    results = ingestion.ingest(datasets=['global_mean'])
    
    # Push results to XCom for downstream tasks
    context['ti'].xcom_push(key='nasa_files', value=results)
    
    logger.info(f"NASA ingestion complete: {results}")
    return results


def ingest_noaa_co2(**context):
    """Task to ingest NOAA CO2 data."""
    logger.info("Starting NOAA CO2 data ingestion")
    
    ingestion = NOAACO2Ingestion(output_dir='/data/raw')
    results = ingestion.ingest(datasets=['annual_mean'])
    
    context['ti'].xcom_push(key='co2_files', value=results)
    
    logger.info(f"CO2 ingestion complete: {results}")
    return results


def ingest_noaa_methane(**context):
    """Task to ingest NOAA methane data."""
    logger.info("Starting NOAA methane data ingestion")
    
    ingestion = NOAAMethaneIngestion(output_dir='/data/raw')
    results = ingestion.ingest(datasets=['annual_mean'])
    
    context['ti'].xcom_push(key='methane_files', value=results)
    
    logger.info(f"Methane ingestion complete: {results}")
    return results


def ingest_noaa_sealevel(**context):
    """Task to ingest NOAA sea level data."""
    logger.info("Starting NOAA sea level data ingestion")
    
    ingestion = NOAASeaLevelIngestion(output_dir='/data/raw')
    results = ingestion.ingest()
    
    context['ti'].xcom_push(key='sealevel_files', value=results)
    
    logger.info(f"Sea level ingestion complete: {results}")
    return results


def validate_ingestion(**context):
    """Task to validate that all ingestion tasks completed successfully."""
    ti = context['ti']
    
    nasa_files = ti.xcom_pull(key='nasa_files', task_ids='ingest_nasa_temperature')
    co2_files = ti.xcom_pull(key='co2_files', task_ids='ingest_noaa_co2')
    methane_files = ti.xcom_pull(key='methane_files', task_ids='ingest_noaa_methane')
    sealevel_files = ti.xcom_pull(key='sealevel_files', task_ids='ingest_noaa_sealevel')
    
    all_files = {
        'nasa': nasa_files,
        'co2': co2_files,
        'methane': methane_files,
        'sealevel': sealevel_files
    }
    
    logger.info(f"Validation results: {all_files}")
    
    # Check if all ingestions were successful
    failed = [k for k, v in all_files.items() if not v]
    
    if failed:
        raise ValueError(f"Failed ingestion tasks: {failed}")
    
    logger.info("All ingestion tasks completed successfully")
    return all_files


# Define tasks
task_nasa = PythonOperator(
    task_id='ingest_nasa_temperature',
    python_callable=ingest_nasa_temperature,
    dag=dag,
)

task_co2 = PythonOperator(
    task_id='ingest_noaa_co2',
    python_callable=ingest_noaa_co2,
    dag=dag,
)

task_methane = PythonOperator(
    task_id='ingest_noaa_methane',
    python_callable=ingest_noaa_methane,
    dag=dag,
)

task_sealevel = PythonOperator(
    task_id='ingest_noaa_sealevel',
    python_callable=ingest_noaa_sealevel,
    dag=dag,
)

task_validate = PythonOperator(
    task_id='validate_ingestion',
    python_callable=validate_ingestion,
    dag=dag,
)

# Define task dependencies
# All ingestion tasks run in parallel, then validation
[task_nasa, task_co2, task_methane, task_sealevel] >> task_validate

# Optional: Trigger transformation pipeline after successful ingestion
task_trigger_transformation = BashOperator(
    task_id='trigger_transformation',
    bash_command='airflow dags trigger climate_data_transformation',
    dag=dag,
)

task_validate >> task_trigger_transformation
