from flask import Flask
from flask_cors import CORS
from waitress import serve
from db import init_db
from auth import auth_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
init_db(app)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
