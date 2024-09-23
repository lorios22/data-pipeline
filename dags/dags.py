"""
This script defines a DAG (Directed Acyclic Graph) in Apache Airflow used to perform web scraping, preprocess the resulting JSON files,
and insert the data into a database. The DAG is scheduled to run daily and follows a simple sequence of tasks:
web scraping, JSON file preprocessing, and database insertion.

Main Components:
- **DAG**: Defines the workflow structure and schedule.
- **PythonOperator**: Executes Python functions as tasks in the DAG.
- **WebScraper**: A class imported from the `webscraper` module, responsible for scraping data from a specified URL.
- **preprocessing_json_from_directory**: Function from the `preprocessing` module, used to preprocess JSON files in a directory.
- **insert_into_db**: Function from the `database` module, used to insert processed data into a database.
- **default_args**: Default parameters applied to all tasks in the DAG, such as retry behavior and email notifications.

DAG Configuration:
- **owner**: Specifies the owner of the DAG ('airflow').
- **depends_on_past**: Set to `False`, meaning each run of the DAG does not depend on previous runs.
- **email_on_failure**/**email_on_retry**: Disable email notifications for task failure or retry.
- **retries**: Number of times a task will retry in case of failure.
- **retry_delay**: Specifies the wait time between retries (5 minutes).

Defined Tasks:
1. **run_webscraper**: Executes the `WebScraper` class to scrape data from a specified URL.
2. **run_preprocessing**: Calls the `preprocessing_json_from_directory` function to preprocess scraped JSON files.
3. **insert_into_db**: Inserts preprocessed data (in CSV format) into a database.

Task Dependencies:
- The DAG begins with the web scraping task (`run_webscraper`), followed by preprocessing the scraped JSON files (`run_preprocessing`).
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Ensure the script directory is included in Python's path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from preprocessing import preprocessing_json_from_directory
from webscraper import WebScraper
from database import insert_into_db

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',  # Owner of the DAG
    'depends_on_past': False,  # Does not depend on previous DAG runs
    'email_on_failure': False,  # Disable email notifications on failure
    'email_on_retry': False,  # Disable email notifications on retry
    'retries': 1,  # Number of retries in case of failure
    'retry_delay': timedelta(minutes=5),  # Time to wait between retries
}

# Create the DAG
with DAG(
    'preprocessing_and_webscraping_dag',
    default_args=default_args,
    description='DAG to run web scraping and process a JSON file',  # Description of the DAG
    schedule_interval=timedelta(days=1),  # Schedule interval (daily)
    start_date=datetime(2024, 9, 11),  # Start date for the DAG
    catchup=False,  # Do not run past DAG instances
) as dag:

    # Function to run the web scraper
    def run_webscraper():
        url = "https://vitalik.eth.limo/"
        scraper = WebScraper(url, verbose=True, save_to_file=True, save_format='json')  # Enable verbose mode for debugging
        scraper.scrape()  # Run the web scraper

    # Task to execute the web scraper
    scrape_task = PythonOperator(
        task_id='run_webscraper',  # Task ID for the web scraper
        python_callable=run_webscraper,  # Python function to be executed
    )

    # Function to preprocess the scraped JSON files and save as CSV
    def preprocessing_and_save():
        webscraping_dir = '/opt/airflow/dags/files/webscraper'  # Directory where web scraping output is stored
        preprocessed_dir = '/opt/airflow/dags/files/preprocessed'  # Directory to save preprocessed output
        preprocessing_json_from_directory(webscraping_dir)  # Run the preprocessing function

    # Task to run preprocessing
    run_preprocessing = PythonOperator(
        task_id='run_preprocessing',  # Task ID for preprocessing
        python_callable=preprocessing_and_save,  # Python function to be executed
    )

    # Task to insert preprocessed data into the database
    insert_task = PythonOperator(
        task_id='insert_into_db',  # Task ID for database insertion
        python_callable=insert_into_db,  # Python function to be executed
        op_args=['/opt/airflow/dags/files/preprocessed/titulos.csv']  # Path to the CSV file to be inserted into the database
    )

    # Task dependencies: run web scraper first, then preprocessing
    scrape_task >> run_preprocessing  # >> insert_task (uncomment if insert step is added)