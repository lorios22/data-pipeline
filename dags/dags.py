"""
This script defines a DAG (Directed Acyclic Graph) in Apache Airflow used to execute preprocessing tasks on a JSON file.
The DAG is scheduled to run daily and performs two main functions: preprocessing a JSON file and saving the results
to a CSV file. The script uses Python operators (PythonOperator) to define tasks in Airflow and manage the execution
of the workflow.

Main Components:
- DAG: Defines the workflow structure and scheduling.
- PythonOperator: Operator that executes Python functions to perform preprocessing and saving tasks.
- preprocessing_json: Function imported from the `preprocessing` module responsible for preprocessing a JSON file.
- save_json_to_csv: Function imported from the `preprocessing` module that saves the preprocessed result in CSV format.
- default_args: Default arguments applied to all tasks within the DAG.

DAG Configuration:
- owner: Owner of the DAG (Airflow).
- depends_on_past: Indicates that DAG runs do not depend on previous runs.
- email_on_failure/email_on_retry: Disables email notifications on failure or retry.
- retries: Number of retries in case of failure.
- retry_delay: Waiting time between retries.

Defined Tasks:
- preprocessing_and_save: Python function that reads a JSON file, preprocesses it, and saves the result to a CSV file.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Ensure the script directory is in Python's path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from preprocessing import preprocessing_json, save_json_to_csv

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
with DAG(
    'preprocessing_json',
    default_args=default_args,
    description='DAG to execute preprocessing of a JSON file',
    schedule_interval=timedelta(days=1),  # Schedule interval (daily)
    start_date=datetime(2024, 9, 11),  # DAG start date
    catchup=False,  # Avoid running past unexecuted jobs
) as dag:

    # Define the Python task that will execute the preprocessing function
    def preprocessing_and_save():
        json_str = preprocessing_json('/opt/airflow/dags/Scrape_Result_2024-09-11-14-25-20.json')
        if json_str:
            save_json_to_csv(json_str, '/opt/airflow/dags/titulos.csv')

    # Create the Airflow task using PythonOperator
    run_preprocessing = PythonOperator(
        task_id='run_preprocessing',  # Task identifier in the DAG
        python_callable=preprocessing_and_save,  # Python function to execute
    )

    # Define the workflow
    run_preprocessing