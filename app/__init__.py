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
    # Configuración base
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # postgresql://user:pass@host:5432/db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')

    # MercadoLibre OAuth
    app.config['ML_CLIENT_ID'] = os.getenv('ML_CLIENT_ID')
    app.config['ML_CLIENT_SECRET'] = os.getenv('ML_CLIENT_SECRET')
    app.config['ML_REDIRECT_URI'] = os.getenv('ML_REDIRECT_URI')

    # Inicializar extensiones
    db.init_app(app)
    login.init_app(app)

    # Redis y RQ
    global redis_conn, task_queue
    redis_conn = Redis.from_url(os.getenv('REDIS_URL'))  # redis://:pass@host:6379
    task_queue = Queue(connection=redis_conn)

    # Registrar blueprints
    from app.auth import auth_bp
    from app.routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
