import json
from io import BytesIO
from openai import OpenAI
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI()

class OpenAIStorageUtils:
    @staticmethod
    def store_json_to_openai(file_name, data):
        """
        This method stores data as a JSON file in OpenAI's storage.
        :param file_name: The name of the file to be saved in OpenAI storage
        :param data: The content to be uploaded (should be a list with one dictionary object)
        :return: Response from OpenAI after file upload
        """
        try:
            # Convert the data to a JSON string and then to bytes
            json_str = json.dumps(data)
            json_bytes = json_str.encode('utf-8')
            json_file = BytesIO(json_bytes)
            json_file.name = file_name

            # Upload the file to OpenAI's storage
            response = client.files.create(
                file=json_file,
                purpose='fine-tune'  # You can adjust the purpose based on your needs
            )
            return response
        except Exception as e:
            print(f"Error storing JSON to OpenAI: {e}")
            return None

    @staticmethod
    def retrieve_json_from_openai(file_id):
        """
        This method retrieves a JSON file from OpenAI storage.
        :param file_id: The ID of the file to be retrieved
        :return: The content of the file as a Python dictionary
        """
        try:
            response = client.files.content(file_id)
            file_content = response.content.decode('utf-8')
            data = json.loads(file_content)
            return data
        except Exception as e:
            print(f"Error retrieving JSON from OpenAI: {e}")
            return None

    @staticmethod
    def check_file_exists(hash_key):
        """
        This method checks if a file with a specific hash_key already exists in OpenAI storage.
        :param hash_key: The unique hash key to check in existing files
        :return: True if a file with the hash_key exists, False otherwise
        """
        try:
            files = client.files.list()
            for file in files.data:
                file_id = file.id
                file_content = OpenAIStorageUtils.retrieve_json_from_openai(file_id)
                if file_content and isinstance(file_content, list):
                    if len(file_content) > 0 and file_content[0].get('hash_key') == hash_key:
                        return True
            return False
        except Exception as e:
            print(f"Error checking file existence: {e}")
            return False

    @staticmethod
    def delete_files_from_openai(hash_key):
        """
        This method deletes files that match the specified hash_key from OpenAI's storage.
        :param hash_key: The unique hash key used to identify the files to delete
        :return: A list of deleted file IDs
        """
        deleted_files = []
        try:
            files = client.files.list()
            file_ids_to_delete = []

            # Find the files to delete based on the hash_key
            for file in files.data:
                file_id = file.id
                file_content = OpenAIStorageUtils.retrieve_json_from_openai(file_id)
                if file_content and isinstance(file_content, list):
                    if len(file_content) > 0 and file_content[0].get('hash_key') == hash_key:
                        file_ids_to_delete.append(file_id)

            # Use ThreadPoolExecutor to delete files concurrently
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(OpenAIStorageUtils._delete_single_file, file_id) for file_id in
                           file_ids_to_delete]
                for future in futures:
                    result = future.result()
                    if result:
                        deleted_files.append(result)

            return deleted_files

        except Exception as e:
            print(f"Error deleting files for hash_key {hash_key}: {e}")
            return deleted_files

    @staticmethod
    def _delete_single_file(file_id):
        """
        Helper method to delete a single file from OpenAI storage.
        :param file_id: The ID of the file to delete
        :return: The file ID if deletion is successful, else None
        """
        try:
            client.files.delete(file_id)
            return file_id
        except Exception as e:
            print(f"Error deleting file {file_id}: {e}")
            return None
