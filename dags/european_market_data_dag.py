from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
# Import the main function from the base script
from functions.financial_market_tracker.webscarper import save_market_data_to_file
from dags.functions.general_functions.upload_files import upload_preprocessed_files_to_vector_store

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG for the European market
with DAG(
    'european_market_closing_data_retrieval',
    default_args=default_args,
    description='DAG to extract data for the European market',
    schedule_interval='0 16 * * 1-5',  # Runs at 4:00 PM UTC (Monday to Friday)
    catchup=False
) as dag:

    # Define the output paths for the .txt file
    output_path = "/opt/airflow/dags/files/preprocessed/european_market_closing_data.txt"
    local_path = "/opt/airflow/files/european_market_closing_data.txt"

    # Task to extract European market data
    def run_european_market_data():
        """
        Runs the main function that retrieves and saves the European market data.

        This function writes the closing market data to two file paths: one in the 
        preprocessed directory and a local copy.
        """
        save_market_data_to_file(output_path)
        save_market_data_to_file(local_path)

    # Create the PythonOperator task to extract European market closing data
    extract_european_market_closing_data = PythonOperator(
        task_id='extract_european_market_closing_data',
        python_callable=run_european_market_data,
        dag=dag
    )

    # Define the function to upload preprocessed files to the vector store
    def upload_preprocessed_files():
        """
        Uploads the preprocessed files (in CSV format) to the vector store.

        This function uploads the preprocessed market data files to the vector store,
        calling the 'upload_preprocessed_files_to_vector_store()' function.
        """
        upload_preprocessed_files_to_vector_store()

    # Task to upload the preprocessed files to the vector store
    upload_files_task = PythonOperator(
        task_id='upload_preprocessed_files',
        python_callable=upload_preprocessed_files,  # Python function to be executed
    )

    # Set the task dependencies: first extract market data, then upload the files
    extract_european_market_closing_data >> upload_files_task