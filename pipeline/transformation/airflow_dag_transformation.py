"""
Airflow DAG for Climate Data Transformation Pipeline
Orchestrates data cleaning, merging, and feature engineering
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.dates import days_ago
from datetime import timedelta
import logging

# Import custom transformation module
import sys
sys.path.append('/opt/airflow/dags')

from data_transformer import ClimateDataTransformer

logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'climate_team',
    'depends_on_past': True,
    'email': ['climate-alerts@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1),
}

# Define the DAG
dag = DAG(
    'climate_data_transformation',
    default_args=default_args,
    description='Transform and clean ingested climate data',
    schedule_interval='0 3 * * *',  # Run daily at 3 AM (after ingestion)
    start_date=days_ago(1),
    catchup=False,
    tags=['climate', 'transformation', 'etl'],
)


def run_transformation(**context):
    """Task to run data transformation."""
    logger.info("Starting data transformation")
    
    transformer = ClimateDataTransformer(
        input_dir='/data/raw',
        output_dir='/data/processed'
    )
    
    output_file = transformer.transform()
    
    # Push results to XCom
    context['ti'].xcom_push(key='processed_file', value=output_file)
    
    logger.info(f"Transformation complete: {output_file}")
    return output_file


def validate_transformation(**context):
    """Task to validate transformation results."""
    import pandas as pd
    
    ti = context['ti']
    processed_file = ti.xcom_pull(key='processed_file', task_ids='transform_data')
    
    if not processed_file:
        raise ValueError("No processed file found")
    
    # Load and validate the processed data
    df = pd.read_csv(processed_file)
    
    # Check if required columns exist
    required_columns = ['year', 'temp_anomaly_c', 'co2_ppm', 'methane_ppb', 'sea_level_mm']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Check for data quality
    if len(df) < 10:
        raise ValueError(f"Insufficient data: only {len(df)} records")
    
    if df['year'].duplicated().any():
        raise ValueError("Duplicate years found in processed data")
    
    logger.info(f"Validation passed: {len(df)} records, {len(df.columns)} columns")
    
    return {
        'record_count': len(df),
        'column_count': len(df.columns),
        'year_range': (df['year'].min(), df['year'].max())
    }


# Wait for ingestion DAG to complete
wait_for_ingestion = ExternalTaskSensor(
    task_id='wait_for_ingestion',
    external_dag_id='climate_data_ingestion',
    external_task_id='validate_ingestion',
    timeout=3600,
    allowed_states=['success'],
    failed_states=['failed', 'skipped'],
    mode='reschedule',
    dag=dag,
)

# Transform data
task_transform = PythonOperator(
    task_id='transform_data',
    python_callable=run_transformation,
    dag=dag,
)

# Validate transformation
task_validate = PythonOperator(
    task_id='validate_transformation',
    python_callable=validate_transformation,
    dag=dag,
)

# Generate data quality report
task_quality_report = BashOperator(
    task_id='generate_quality_report',
    bash_command='python /opt/airflow/dags/generate_quality_report.py',
    dag=dag,
)

# Define task dependencies
wait_for_ingestion >> task_transform >> task_validate >> task_quality_report

# Optional: Trigger ML pipeline after successful transformation
task_trigger_ml = BashOperator(
    task_id='trigger_ml_pipeline',
    bash_command='airflow dags trigger climate_ml_pipeline',
    dag=dag,
)

task_quality_report >> task_trigger_ml
