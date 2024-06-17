from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})
app.config["MONGO_URI"] = "mongodb://localhost:27017/ascend-edu"
mongo = PyMongo(app)
db = mongo.db

if __name__ == '__main__':
    from routes.upload_bp import upload_bp
    app.register_blueprint(upload_bp)

    from routes.file_bp import file_bp
    app.register_blueprint(file_bp)

    from routes.delete_bp import delete_bp
    app.register_blueprint(delete_bp)

    app.run(debug=True)
