import pandas as pd
import re
import json  # Asegurarse de importar la biblioteca json

file_path = '/opt/airflow/dags/Scrape_Result_2024-09-11-14-25-20.json'

def preprocessing_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Verificar si el archivo está vacío
    if not content.strip():
        print("El archivo está vacío o solo contiene espacios en blanco.")
        return None  # Retornar None si el archivo está vacío
    else:
        # Limpiar el contenido eliminando cualquier carácter no imprimible
        cleaned_content_filtered = ''.join(char for char in content if char.isprintable())

        # Reemplazar comillas simples por comillas dobles para hacer el JSON válido
        cleaned_content_filtered = re.sub(r"(?<!\\)'", '"', cleaned_content_filtered)

        # Intentar extraer JSON solo desde donde parece comenzar
        json_start = cleaned_content_filtered.find('{')
        if json_start != -1:
            json_content = cleaned_content_filtered[json_start:]  # Intentar extraer desde donde comienza JSON
        
            try:
                # Convertir el contenido a un objeto JSON
                json_data = json.loads(json_content)
            
                # Extraer títulos de 'entries'
                titles = [entry.get('title', '') for entry in json_data.get('entries', [])]

                # Crear un DataFrame con los títulos
                df_titles = pd.DataFrame(titles, columns=['Title'])

                # Convertir el DataFrame a un string JSON serializable
                json_serializable_df = df_titles.to_json(orient='split')

                # Mostrar el DataFrame como JSON serializable string
                print(json_serializable_df)
                return json_serializable_df

            except json.JSONDecodeError as e:
                print(f"Error al decodificar JSON después de la limpieza: {e}")

                # Intentar extracción con expresiones regulares como respaldo
                title_pattern = re.compile(r'"title":\s*"([^"]+)"')  # Patrón para encontrar los títulos en el texto
                titles = title_pattern.findall(cleaned_content_filtered)  # Extraer todos los títulos coincidentes
            
                # Crear un DataFrame con los títulos
                df_titles = pd.DataFrame(titles, columns=['Title'])

                # Convertir el DataFrame a un string JSON serializable
                json_serializable_df = df_titles.to_json(orient='split')

                # Mostrar el DataFrame como JSON serializable string
                print(json_serializable_df)
                return json_serializable_df
        else:
            print("No se encontró un JSON válido en el contenido del archivo.")
            return None  # Retornar None si no se encuentra un JSON válido

def save_json_to_csv(json_str, file_name):
    """
    Guarda un JSON serializable en un archivo CSV.
    
    :param json_str: Cadena JSON que representa un DataFrame
    :param file_name: Nombre del archivo CSV
    """
    if json_str:
        df = pd.read_json(json_str, orient='split')
        df.to_csv(file_name, index=False, encoding='utf-8')
        print(f"DataFrame guardado como {file_name}")
    else:
        print("La cadena JSON está vacía o es inválida. No se guardó ningún archivo.")