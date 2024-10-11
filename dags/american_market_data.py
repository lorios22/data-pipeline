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

# Define the DAG for the American market
with DAG(
    'american_market_closing_data_retrieval',
    default_args=default_args,
    description='DAG to extract data for the American market',
    schedule_interval='30 21 * * 1-5',  # Runs at 9:30 PM UTC (Monday to Friday)
    catchup=False
) as dag: 

    # Define the output path for the .txt file
    output_path = "/opt/airflow/dags/files/preprocessed/american_market_closing_data.txt"
    local_path = "/opt/airflow/files/american_market_closing_data.txt"

    # Define the task that calls the main function from the base script
    def run_american_market_data():
        """
        Runs the main function that retrieves and saves the American market data.
        
        This function writes the market closing data to two different file paths: 
        one in the preprocessed directory and another local copy.
        """
        save_market_data_to_file(output_path)
        save_market_data_to_file(local_path)
    
    # Create the PythonOperator task to extract American market data
    extract_american_closing_market_data = PythonOperator(
        task_id='extract_american_closing_market_data',
        python_callable=run_american_market_data,
        dag=dag
    )

    # Define the function to upload preprocessed files to the vector store
    def upload_preprocessed_files():
        """
        Uploads the preprocessed files (in CSV format) to the vector store.
        
        This function assumes the files have been saved in a predefined directory,
        and it uses the function 'upload_preprocessed_files_to_vector_store()' 
        to handle the upload process.
        """
        upload_preprocessed_files_to_vector_store()  # Call the function to upload files

    # Task to upload files to the vector store
    upload_files_task = PythonOperator(
        task_id='upload_preprocessed_files',
        python_callable=upload_preprocessed_files,  # Python function to be executed
    )
    
    # Set the task dependencies: first extract market data, then upload files
    extract_american_closing_market_data >> upload_files_task
