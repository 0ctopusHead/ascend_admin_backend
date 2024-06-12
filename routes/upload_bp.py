from flask import Blueprint, request, jsonify
from controller.FileController import FileController
from controller.EmbeddedController import EmbeddedController
upload_bp = Blueprint('upload_bp', __name__)


@upload_bp.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    file_controller = FileController()
    embedding_controller = EmbeddedController()
    response_data, status_code = file_controller.upload_files(files)
    embedding_response, embedding_status = embedding_controller.trigger_embedding_process()

    upload_message = response_data.get_json()
    upload_message = upload_message.get('message')
    embedded_message = embedding_response.get_json()
    embedded_message = embedded_message.get('message')
    return jsonify(
        {'upload_response': f'{upload_message}',
         'upload_status': f'{status_code}',
         'embedded_response': f'{embedded_message}',
         'embedded_status': f'{embedding_status}'})


@upload_bp.route('/upload_by_url', methods=['POST'])
def upload_by_url():
    user_request = request.get_json()
    pdf_urls = user_request.get("urls")
    file_controller = FileController()
    response_data, status_code = file_controller.upload_urls(pdf_urls)
    return response_data, status_code
