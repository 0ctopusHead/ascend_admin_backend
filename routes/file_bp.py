from flask import Blueprint, request, jsonify
from controller.FileController import FileController

file_bp = Blueprint('file_bp', __name__)


@file_bp.route('/get_files', methods=['GET'])
def get_files():
    file_controller = FileController()
    response_data = file_controller.get_files()
    return response_data
