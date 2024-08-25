import json
from io import BytesIO
from openai import OpenAI
import requests
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI()
class OpenAIStorageUtils:
    @staticmethod
    def store_json_to_openai(file_name, data):
        json_str = json.dumps(data)
        json_bytes = json_str.encode('utf-8')
        json_file = BytesIO(json_bytes)
        json_file.name = file_name
        response = client.files.create(
            file=json_file,
            purpose='fine-tune'
        )
        return response


    @staticmethod
    def retrieve_json_from_openai(file_id):
        response = client.files.content(file_id)
        file_content = response.content.decode('utf-8')
        data = json.loads(file_content)
        return data

    @staticmethod
    def check_file_exists(hash_key):
        files = client.files.list()
        for file in files.data:
            file_id = file.id
            file_content = OpenAIStorageUtils.retrieve_json_from_openai(file_id)
            if file_content is None:
                continue

            if isinstance(file_content, list):  # Make sure it's a list of dictionaries
                for content in file_content:
                    print("content: " + str(content))  # Debugging
                    if 'hash_key' in content and content['hash_key'] == str(hash_key):
                        return True
            else:
                print(f"Unexpected file content format: {file_content}")
        return False

    @staticmethod
    def delete_files_from_openai(hash_key):
        deleted_files = []
        try:
            # List all files stored in OpenAI
            files = client.files.list()
            for file in files.data:
                file_id = file.id
                file_content = OpenAIStorageUtils.retrieve_json_from_openai(file_id)
                if file_content is None:
                    continue

                # Handle both cases where file_content is a dictionary or a list of dictionaries
                if isinstance(file_content, list):
                    # If the content is a list, iterate through each dictionary
                    for content in file_content:
                        if 'hash_key' in content and content['hash_key'] == str(hash_key):
                            # Delete the file from OpenAI storage
                            client.files.delete(file_id)
                            deleted_files.append(file_id)
                            break  # Stop checking other content in the same file
                elif isinstance(file_content, dict):
                    # If the content is a single dictionary
                    if 'hash_key' in file_content and file_content['hash_key'] == str(hash_key):
                        # Delete the file from OpenAI storage
                        client.files.delete(file_id)
                        deleted_files.append(file_id)
                else:
                    print(f"Unexpected file content format: {file_content}")

            return deleted_files
        except Exception as e:
            print(f"An error occurred while deleting the files: {e}")
            return deleted_files