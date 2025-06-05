from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy

mysql = MySQL()
db = SQLAlchemy()

def init_db(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Data@123'
    app.config['MYSQL_DB'] = 'prabha'
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    mysql.init_app(app)

  # SQLAlchemy (ORM)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Data%40123@localhost/prabha'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)