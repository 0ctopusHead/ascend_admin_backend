from service.FileService import FileService
from service.EmbeddedService import EmbeddedService
from PyPDF2.errors import PdfReadError
from requests.exceptions import MissingSchema, HTTPError, ConnectionError


class FileController:
    def __init__(self):
        self.file_service = FileService()
        self.embedded_service = EmbeddedService()

    def upload_files(self, files):
        try:
            response_data, status_code = self.file_service.upload(files)
            return response_data, status_code
        except ValueError as e:
            return str(e), 400
        except FileNotFoundError as e:
            return 'Could not find the file', 400
        except AttributeError as e:
            return str(e), 400
        except PdfReadError as e:
            return "The file is not a PDF file", 400

    def upload_urls(self, urls):
        try:
            response_data, status_code = self.file_service.upload_urls(urls)
            self.trigger_embedding_process()
            return response_data, status_code
        except MissingSchema as e:
            return 'Invalid URL, Please recheck your URL', 400
        except ValueError as e:
            return str(e), 400
        except FileNotFoundError as e:
            return str(e), 400
        except AttributeError as e:
            return str(e), 400
        except ConnectionError as e:
            return 'Could not connect with the URL', 503
        except HTTPError as e:
            return 'The URL provided is not found (404). Please check the URL and try again', 404

    def delete_files(self, files_id):
        try:
            response_data, status_code = self.file_service.delete_by_ids(files_id)
            return response_data, status_code
        except ValueError as e:
            return str(e), 400

    def trigger_embedding_process(self):
        embedding_response, embedding_status = self.embedded_service.embedding_files()
        return embedding_response, embedding_status
