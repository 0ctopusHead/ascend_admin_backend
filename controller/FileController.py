from service.FileService import FileService
from service.EmbeddedService import EmbeddedService
from PyPDF2.errors import PdfReadError


class FileController:
    def __init__(self):
        self.file_service = FileService()
        self.embedded_service = EmbeddedService()

    def upload_files(self, files):
        try:
            response_data, status_code = self.file_service.upload(files)
            self.trigger_embedding_process()
            return response_data, status_code
        except ValueError as e:
            return str(e), 400
        except FileNotFoundError as e:
            return 'Could not find the file/ No file attached', 400
        except AttributeError as e:
            return str(e), 400
        except PdfReadError as e:
            return "File must be in .pdf format", 400

    def upload_urls(self, urls):
        try:
            response_data, status_code = self.file_service.upload_url(urls)
            self.trigger_embedding_process()
            return response_data, status_code
        except ValueError as e:
            return str(e), 400
        except FileNotFoundError as e:
            return str(e), 400
        except AttributeError as e:
            return str(e), 400

    def delete_by_id(self, files_id):
        try:
            response_data, status_code = self.file_service.delete_by_id(files_id)
            return response_data, status_code
        except ValueError as e:
            return str(e), 400

    def get_files(self, page, limit):
        try:
            uploaded_files, total_files = self.file_service.get_uploaded_files(page, limit)
            return uploaded_files, total_files
        except Exception as e:
            return str(e), 400

    def trigger_embedding_process(self):
        embedding_response, embedding_status = self.embedded_service.embedding_files()
        return embedding_response, embedding_status
