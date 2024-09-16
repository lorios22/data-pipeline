"""
This script provides two main functions for preprocessing a JSON file and saving the processed data to a CSV file.
The preprocessing involves cleaning and extracting relevant information from the JSON content, specifically titles,
and converting them into a JSON-serializable format. The processed JSON is then saved as a CSV file using Pandas.

Key Components:
- Libraries: Uses `pandas` for DataFrame operations, `re` for regular expression handling, and `json` for JSON operations.
- preprocessing_json: Function that reads a JSON file, cleans the content, extracts titles, and converts the extracted
  information into a JSON-serializable string. It handles both valid JSON structures and fallback extraction using regular expressions.
- save_json_to_csv: Function that takes a JSON-serializable string representing a DataFrame and saves it to a CSV file.

Functions:
1. preprocessing_json(file_path):
   - Reads the content of a JSON file.
   - Checks if the file is empty or contains only whitespace.
   - Cleans the content by removing non-printable characters and replacing single quotes with double quotes for JSON validity.
   - Extracts JSON content from the cleaned text and converts it to a DataFrame.
   - If JSON extraction fails, attempts a fallback extraction using regular expressions.
   - Returns the JSON-serializable string representation of the DataFrame or None if no valid JSON is found.

2. save_json_to_csv(json_str, file_name):
   - Takes a JSON-serializable string representing a DataFrame.
   - Converts the JSON string to a DataFrame and saves it as a CSV file.
   - Prints a message indicating success or failure.

Usage:
- Ensure that the `json` library is imported for JSON operations.
- Adjust the `file_path` to point to the location of the JSON file you want to preprocess.
"""

import pandas as pd
import re
import json  # Ensure to import the json library

file_path = '/opt/airflow/dags/Scrape_Result_2024-09-11-14-25-20.json'

def preprocessing_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Check if the file is empty
    if not content.strip():
        print("The file is empty or only contains whitespace.")
        return None  # Return None if the file is empty
    else:
        # Clean content by removing any non-printable characters
        cleaned_content_filtered = ''.join(char for char in content if char.isprintable())

        # Replace single quotes with double quotes to make JSON valid
        cleaned_content_filtered = re.sub(r"(?<!\\)'", '"', cleaned_content_filtered)

        # Attempt to extract JSON only from where it appears to start
        json_start = cleaned_content_filtered.find('{')
        if json_start != -1:
            json_content = cleaned_content_filtered[json_start:]  # Try extracting from where JSON starts
        
            try:
                # Convert content to a JSON object
                json_data = json.loads(json_content)
            
                # Extract titles from 'entries'
                titles = [entry.get('title', '') for entry in json_data.get('entries', [])]

                # Create a DataFrame with the titles
                df_titles = pd.DataFrame(titles, columns=['Title'])

                # Convert the DataFrame to a JSON serializable string
                json_serializable_df = df_titles.to_json(orient='split')

                # Display the DataFrame as a JSON serializable string
                print(json_serializable_df)
                return json_serializable_df

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON after cleaning: {e}")

                # Attempt extraction with regular expressions as a fallback
                title_pattern = re.compile(r'"title":\s*"([^"]+)"')  # Pattern to find titles in the text
                titles = title_pattern.findall(cleaned_content_filtered)  # Extract all matching titles
            
                # Create a DataFrame with the titles
                df_titles = pd.DataFrame(titles, columns=['Title'])

                # Convert the DataFrame to a JSON serializable string
                json_serializable_df = df_titles.to_json(orient='split')

                # Display the DataFrame as a JSON serializable string
                print(json_serializable_df)
                return json_serializable_df
        else:
            print("No valid JSON found in the file content.")
            return None  # Return None if no valid JSON is found

def save_json_to_csv(json_str, file_name):
    """
    Saves a JSON-serializable string to a CSV file.
    
    :param json_str: JSON string representing a DataFrame
    :param file_name: Name of the CSV file
    """
    if json_str:
        df = pd.read_json(json_str, orient='split')
        df.to_csv(file_name, index=False, encoding='utf-8')
        print(f"DataFrame saved as {file_name}")
    else:
        print("The JSON string is empty or invalid. No file was saved.")