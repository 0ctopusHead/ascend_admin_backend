from flask import Blueprint, request
from controller.FileController import FileController

upload_bp = Blueprint('upload_bp', __name__)


@upload_bp.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    file_controller = FileController()
    response_data, status_code = file_controller.upload_files(files)
    return response_data, status_code


@upload_bp.route('/upload_by_url', methods=['POST'])
def upload_by_url():
    user_request = request.get_json()
    pdf_urls = user_request.get("urls")
    file_controller = FileController()
    response_data, status_code = file_controller.upload_urls(pdf_urls)
    return response_data, status_code
