from flask import Blueprint, jsonify
from app import db, redis_conn, task_queue

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return jsonify({'message': 'VelozML backend funcionando'})

@bp.route('/health')
def health():
    # Verificar base de datos y Redis
    try:
        db.session.execute('SELECT 1')
        redis_conn.ping()
        return jsonify({'status': 'healthy'})
    except Exception as e:
        return jsonify({'status': 'error', 'detail': str(e)}), 500
