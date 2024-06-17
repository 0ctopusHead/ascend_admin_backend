from flask import Blueprint, request
from controller.FileController import FileController

delete_bp = Blueprint('delete_bp', __name__)


@delete_bp.route('/delete_by_id', methods=['POST'])
def delete_file():
    files_id = request.get_json()
    files_id = files_id.get("_id")
    file_controller = FileController()
    response_data, status_code = file_controller.delete_by_id(files_id)
    return response_data, status_code
