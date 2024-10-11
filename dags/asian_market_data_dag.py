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

# Define the DAG for the Asian market data retrieval
with DAG(
    'asian_market_closing_data_retrieval',
    default_args=default_args,
    description='DAG to extract data for the Asian market',
    schedule_interval='30 6 * * 1-5',  # Runs at 6:30 AM UTC (Monday to Friday)
    catchup=False
) as dag:

    # Define the output paths for the .txt files (one preprocessed, one local)
    output_path = "/opt/airflow/dags/files/preprocessed/asian_market_closing_data.txt"
    local_path = "/opt/airflow/files/asian_market_closing_data.txt"

    # Define the task to retrieve and save Asian market data
    def run_asian_market_data():
        """
        Retrieves and saves the closing data for the Asian market.

        This function calls 'save_market_data_to_file()' twice to save data in two locations:
        one in the preprocessed directory and one in a local file path.
        """
        save_market_data_to_file(output_path)
        save_market_data_to_file(local_path)

    # Create the PythonOperator task to extract Asian market closing data
    extract_asian_market_closing_data = PythonOperator(
        task_id='extract_asian_market_closing_data',
        python_callable=run_asian_market_data,
        dag=dag
    )

    # Define the function to upload preprocessed files to the vector store
    def upload_preprocessed_files():
        """
        Uploads the preprocessed files (in CSV format) to the vector store.

        The function assumes the files are already located in the preprocessed directory
        and calls 'upload_preprocessed_files_to_vector_store()' to handle the upload process.
        """
        upload_preprocessed_files_to_vector_store()  # Call the function to upload files

    # Create the PythonOperator task to upload files to the vector store
    upload_files_task = PythonOperator(
        task_id='upload_preprocessed_files',
        python_callable=upload_preprocessed_files,  # Python function to be executed
    )

    # Define the task dependencies: first extract market data, then upload the files
    extract_asian_market_closing_data >> upload_files_task
