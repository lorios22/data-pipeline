from sqlalchemy import create_engine
import pandas as pd

def insert_into_db(file_path):
    engine = create_engine('postgresql+psycopg2://airflow:airflow@postgres:5432/airflow')  # Replace 'localhost' with 'postgres'
    
    df = pd.read_csv(file_path)
    
    df.to_sql('my_table', engine, if_exists='replace', index=False)
