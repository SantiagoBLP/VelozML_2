import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from redis import Redis
from rq import Queue

# Extensiones globales
db = SQLAlchemy()
login = LoginManager()
redis_conn = None
task_queue = None


def create_app():
    app = Flask(__name__)
    # Configuración básica
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

    # Inicializar extensiones
    db.init_app(app)
    login.init_app(app)

    # Redis y RQ
    global redis_conn, task_queue
    redis_conn = Redis.from_url(os.getenv('REDIS_URL'))
    task_queue = Queue(connection=redis_conn)

    # Registrar rutas
    from app.routes import bp
    app.register_blueprint(bp)

    return app
