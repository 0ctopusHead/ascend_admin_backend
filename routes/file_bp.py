from flask import Blueprint, request, jsonify
from controller.FileController import FileController

file_bp = Blueprint('file_bp', __name__)


@file_bp.route('/get_files', methods=['GET'])
def get_files():
    limit = request.args.get('_limit', type=int)
    page = request.args.get('_page', type=int)
    file_controller = FileController()
    uploaded_files, total_files = file_controller.get_files(page, limit)
    response = jsonify(uploaded_files)
    response.headers['x-total-count'] = total_files
    print('Total Files:', total_files)
    return response
