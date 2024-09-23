"""
This script contains functions for preprocessing JSON files from a directory, transforming them into CSV format, 
and handling potential issues with the JSON structure. The main function, `preprocessing_json_from_directory`, 
processes the most recent JSON file in a specified directory and converts it into a structured CSV file. 
The function also includes error handling for common JSON issues.

Main Components:
- `get_latest_json_file`: Retrieves the most recent JSON file from a directory.
- `preprocessing_json_from_directory`: Main function that preprocesses the latest JSON file, corrects some common formatting issues,
   extracts relevant data (like URLs and titles), and saves the results to a CSV file.
- Error Handling: The function handles JSON decoding errors and provides debugging information when issues arise.

Key Steps in `preprocessing_json_from_directory`:
1. Reads the latest JSON file from a given directory.
2. Skips the first 267 lines and preprocesses the content (correcting quotes, null values, and other formatting issues).
3. Extracts the 'links' section from the JSON and structures it into rows with 'title', 'date', and 'url'.
4. Saves the processed data into a CSV file.
5. Deletes the original JSON file after successful processing.
6. Handles and logs any errors that occur during processing, including JSON decoding issues.

The output CSV file is saved with a timestamped filename, ensuring uniqueness, and it is stored in the specified output directory.
"""
import os 
import pandas as pd
import json
import datetime
import csv

# Function to get the latest JSON file in a directory
def get_latest_json_file(directory):
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]  # Get all JSON files
    if not json_files:
        print("No JSON files found in the directory.")
        return None

    # Sort files by modification time, latest first
    json_files.sort(key=lambda x: os.path.getmtime(os.path.join(directory, x)), reverse=True)
    latest_file = json_files[0]
    return os.path.join(directory, latest_file)

# Main function to preprocess the latest JSON file from a directory
def preprocessing_json_from_directory(directory, start_index=268):
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
        content_from_start = content_from_start.replace("\'s", '')
        content_from_start = content_from_start.replace("n't", ' t')
        content_from_start = content_from_start.replace("\ ", '')
        content_from_start = content_from_start.replace("'", '"')  # Replace single quotes with double quotes
        content_from_start = content_from_start.replace("None", "null")  # Replace Python None with JSON null
        content_from_start = content_from_start.replace('"pro-crypto"', '\\"pro-crypto\\"')
        content_from_start = content_from_start.replace('Ethereum network"s', 'Ethereum network\'s')  # Correct quotation
        content_from_start = content_from_start.replace('Vitalik Buterin"s', 'Vitalik Buterin\'s')  # Correct quotation
        content_from_start = content_from_start.replace('tructured_data', '"structured_data')

        # Fix boolean values for JSON compatibility
        content_from_start = content_from_start.replace("True", "true").replace("False", "false")
        print(content_from_start[:1000])  # Print the first 1000 characters for debugging

        # Debug problematic sections of the file
        problematic_section = content_from_start[25790:25820]
        print("Problematic section:", problematic_section)

        print("\nShowing more context around the error:")
        print(content_from_start[25750:25850])  # Show a larger range around the problematic section

        # Load the content as JSON data
        json_data = json.loads(content_from_start)
        if 'links' in json_data:
            links = json_data['links']  # Extract links from the JSON
            data = [{'url': link['url'], 'title': link['text']} for link in links]  # Collect title and URL
            for item in data:
                print(f"Title: {item['title']}, URL: {item['url']}")  # Print the title and URL for debugging
        else:
            print("No links found in the JSON file.")
        
        # Prepare rows for CSV output
        rows = []
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # Extract title, date, and link from the JSON data
        for item in data:
            title = item.get('title', 'N/A')
            date = item.get('date', timestamp)
            link = item.get('url', 'N/A')
            rows.append([title, date, link])

        # Define the CSV file path
        csv_file_path = f'/opt/airflow/dags/files/preprocessed/output_{timestamp}.csv'

        # Write the data to the CSV file
        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['Title', 'Date', 'URL'])  # Write CSV header
            writer.writerows(rows)
        
        print(f"CSV file saved at {csv_file_path}")
        
        # Remove the processed JSON file
        os.remove(file_path)
        print(f"JSON file {file_path} deleted after processing.")

    except json.JSONDecodeError as json_error:
        print(f"Error decoding JSON: {json_error}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
