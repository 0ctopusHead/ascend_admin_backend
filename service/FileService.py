import os
from bson import ObjectId
import base64
import requests
from urllib.parse import urlparse
from io import BytesIO
import PyPDF2
from app import mongo
from flask import jsonify
db = mongo.db


class FileService:
    def __init__(self):
        self.encoded_files = {}
        self.reader = PyPDF2
        self.database = db

    def upload(self, files_data):
        if not files_data:
            raise FileNotFoundError
        pdf_file_paths = self.save_files_to_disk(files_data)
        encoded_files = self.encode_pdf(pdf_file_paths)

        for file_name, encoded_data in encoded_files.items():
            db.EncodedPDF.insert_one(encoded_data)

        for file_path in pdf_file_paths:
            os.remove(file_path)
        return jsonify({'message': 'Upload files success'}), 200

    def upload_url(self, urls):
        encoded_pdfs = self.encode_url(urls)
        for file_name, file_data in encoded_pdfs.items():
            db.EncodedPDF.insert_one(file_data)
        return jsonify({'message': 'Upload from URL success'}), 200

    def delete_by_id(self, files_id):
        try:
            for file_id in files_id:
                encoded_file = self.database.EncodedPDF.find_one({"_id": ObjectId(file_id)})
                if encoded_file:
                    hash_key = encoded_file.get('hash_key')
                    deleted_file = self.database.EncodedPDF.delete_one({"_id": ObjectId(file_id)})
                    print(deleted_file.deleted_count)
                    if hash_key:
                        deleted_embedded_file = self.database.EmbeddedPDF.delete_many({"hash_key": hash_key})
                        print(deleted_embedded_file.deleted_count)
                else:
                    raise ValueError(f'Could not find the {file_id} in the database')
            return jsonify({'message': 'Delete success'}), 200
        except Exception as e:
            raise e

    def save_files_to_disk(self, files):
        try:
            pdf_file_paths = []
            if files:
                for file in files:
                    if file and file.filename.endswith('.pdf'):
                        file_path = file.filename
                        file.save(file_path)
                        if self.validate_input_from_file(file_path):
                            pdf_file_paths.append(file_path)
                        else:
                            raise AttributeError("The file must in PDF/A format")
                    else:
                        raise ValueError("Only PDF files are supported.")
            else:
                raise FileNotFoundError
            return pdf_file_paths
        except Exception as e:
            for file in files:
                if file:
                    os.remove(file.filename)
            raise e

    def encode_pdf(self, pdf_file_paths):
        try:
            for pdf_file_path in pdf_file_paths:
                with open(pdf_file_path, 'rb') as pdf:
                    hash_key = ObjectId()
                    encode_string = base64.b64encode(pdf.read()).decode('utf-8')
                    file_name = os.path.basename(pdf_file_path)
                    self.encoded_files[hash_key] = {
                        "file_name": file_name,
                        "encoded_string": encode_string,
                        "hash_key": hash_key
                    }
            return self.encoded_files
        except FileNotFoundError as e:
            raise e

    def encode_url(self, urls):
        for url in urls:
            pdf_data = self.download_pdf_from_url(url)
            if self.validate_input_from_bytes(pdf_data):
                encode_string = base64.b64encode(pdf_data).decode('utf-8')
                file_name = os.path.basename(urlparse(url).path)
                hash_key = ObjectId()
                self.encoded_files[hash_key] = {
                    "file_name": file_name,
                    "encoded_string": encode_string,
                    "hash_key": hash_key
                }
            else:
                raise AttributeError("The file must in PDF/A format")
        return self.encoded_files

    @staticmethod
    def download_pdf_from_url(url):
        try:
            response = requests.get(url)
            if response.headers.get('content-type') == 'application/pdf':
                return response.content
            else:
                raise ValueError("The attached URL is not a PDF URL")
        except Exception as e:
            raise e

    def validate_input_from_file(self, pdf_input):
        try:
            with open(pdf_input, 'rb') as f:
                reader = self.reader.PdfReader(f)
                catalog = reader.trailer['/Root']
                if '/Metadata' in catalog:
                    metadata = catalog['/Metadata'].get_object()
                    if '/Type' in metadata and '/Subtype' in metadata:
                        return metadata['/Type'] == '/Metadata' and metadata['/Subtype'] == '/XML'
            return False
        except Exception as e:
            print(f"Error occurred while validating PDF: {e}")
            raise e

    def validate_input_from_bytes(self, pdf_input):
        try:
            reader = self.reader.PdfReader(BytesIO(pdf_input))
            catalog = reader.trailer['/Root']
            if '/Metadata' in catalog:
                metadata = catalog['/Metadata'].get_object()
                if '/Type' in metadata and '/Subtype' in metadata:
                    return metadata['/Type'] == '/Metadata' and metadata['/Subtype'] == '/XML'
            return False
        except Exception as e:
            print(f"Error occurred while validating PDF: {e}")
            raise e

    def get_uploaded_files(self):
        try:
            uploaded_files_cursor = self.database.EncodedPDF.find({}, {"file_name": 1, "_id": 1})
            uploaded_files = []
            for file in uploaded_files_cursor:
                file["_id"] = str(file["_id"])
                uploaded_files.append(file)
            return uploaded_files
        except Exception as e:
            raise e
