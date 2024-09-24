import os  
import pandas as pd
import json
import datetime
import csv

# Function to get the latest JSON file in a directory
def get_latest_json_file(directory):
    """
    Retrieve the most recent JSON file from the specified directory.

    Args:
        directory (str): The path to the directory containing JSON files.

    Returns:
        str: The full path of the latest JSON file, or None if no JSON files are found.
    """
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]  # Get all JSON files
    if not json_files:
        print("No JSON files found in the directory.")
        return None

    # Sort files by modification time, latest first
    json_files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    latest_file = json_files[0]
    return os.path.join(directory, latest_file)

# Function to save DataFrame to .txt
def save_dataframe_to_txt(df, file_path):
    """
    Save a DataFrame to a text file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        file_path (str): The path where the text file will be saved.
    """
    with open(file_path, 'w') as f:
        f.write(df.to_string(index=False))  # Write the DataFrame to the text file without the index
    print(f"DataFrame saved as .txt at {file_path}")

# Main function to preprocess the latest JSON file from a directory
def preprocessing_json_from_directory(directory, airflow_csv_path, start_index=268):
    """
    Preprocess the latest JSON file from the specified directory and save the results as a text file.

    This function performs the following steps:
    1. Retrieves the most recent JSON file.
    2. Reads and cleans the JSON content.
    3. Converts the cleaned data into a DataFrame.
    4. Saves the DataFrame to a text file in the specified directory.
    5. Deletes the original JSON file after processing.

    Args:
        directory (str): The directory to search for the latest JSON file.
        airflow_csv_path (str): The path to the directory where the output text file will be saved.
        start_index (int, optional): The index to start reading the JSON file. Defaults to 268.
    """
    file_path = get_latest_json_file(directory)  # Get the latest JSON file
    if not file_path:
        return

    try:
        # Open the JSON file and read its contents
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()
            content_from_268 = content[267:]  # Skip the first 267 lines
            print(content_from_268)

        # Join the content, remove problematic characters, and prepare for JSON processing
        content_from_start = ','.join(content_from_268)
        content_from_start = content_from_start.replace("\'s", '')  # Remove problematic apostrophes
        content_from_start = content_from_start.replace("n't", ' t')  # Replace "n't" with " t"
        content_from_start = content_from_start.replace("\ ", '')  # Remove backslashes
        content_from_start = content_from_start.replace("'", '"')  # Replace single quotes with double quotes
        content_from_start = content_from_start.replace("None", "null")  # Replace Python None with JSON null
        content_from_start = content_from_start.replace('"pro-crypto"', '\\"pro-crypto\\"')
        content_from_start = content_from_start.replace('Ethereum network"s', 'Ethereum network\'s')  # Correct quotation
        content_from_start = content_from_start.replace('Vitalik Buterin"s', 'Vitalik Buterin\'s')  # Correct quotation
        content_from_start = content_from_start.replace('tructured_data', '"structured_data')

        # Fix boolean values for JSON compatibility
        content_from_start = content_from_start.replace("True", "true").replace("False", "false")
        print(content_from_start[:1000])  # Print the first 1000 characters for debugging

        # Load the content as JSON data
        json_data = json.loads(content_from_start)
        if 'links' in json_data:
            links = json_data['links']  # Extract links from the JSON
            data = [{'url': link['url'], 'title': link['text']} for link in links]  # Collect title and URL
        else:
            print("No links found in the JSON file.")
            return

        # Create a DataFrame from the data
        df = pd.DataFrame(data)
        df['date'] = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  # Add current timestamp for 'date'

        # Drop rows from 2 to 10 (index positions 1 to 9)
        df.drop(df.index[0:10], inplace=True)

        # Define the Airflow text file path for the output
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        airflow_txt_file_path = os.path.join(airflow_csv_path, f'preprocessed_vitalik_output_{timestamp}.txt')

        # Save DataFrame to a .txt file in Airflow directory
        save_dataframe_to_txt(df, airflow_txt_file_path)

        # Remove the processed JSON file
        os.remove(file_path)
        print(f"JSON file {file_path} deleted after processing.")

    except json.JSONDecodeError as json_error:
        print(f"Error decoding JSON: {json_error}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None