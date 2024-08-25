from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}}, expose_headers=['x-total-count'])
app.config["MONGO_URI"] = "mongodb+srv://ceo_koop:6Y4E3dI980oGC15F@db-mongodb-nyc3-38677-61871e8a.mongo.ondigitalocean.com/ascend-edu?tls=true&authSource=admin&replicaSet=db-mongodb-nyc3-38677"
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
