from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Asegurarse de que el directorio del script esté en el path de Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from preprocessing import preprocessing_json, save_json_to_csv

# Definir los argumentos por defecto de la DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Crear la DAG
with DAG(
    'preprocessing_json',
    default_args=default_args,
    description='DAG para ejecutar el preprocesamiento de un archivo JSON',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 9, 11),
    catchup=False,
) as dag:

    # Definir la tarea de Python que ejecutará la función de preprocesamiento
    def preprocessing_and_save():
        json_str = preprocessing_json('/opt/airflow/dags/Scrape_Result_2024-09-11-14-25-20.json')
        if json_str:
            save_json_to_csv(json_str, '/opt/airflow/dags/titulos.csv')

    run_preprocessing = PythonOperator(
        task_id='run_preprocessing',
        python_callable=preprocessing_and_save,
    )

    # Definir el flujo de trabajo
    run_preprocessing
