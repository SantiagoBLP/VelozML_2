from flask import Blueprint, redirect, request, url_for, current_app
from requests import post
from flask_login import login_user, logout_user, login_required
from app import db, login
from app.models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@auth_bp.route('/login')
def ml_login():
    client_id = current_app.config['ML_CLIENT_ID']
    redirect_uri = current_app.config['ML_REDIRECT_URI']
    auth_url = (
        f"https://auth.mercadolibre.com.ar/authorization"
        f"?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    )
    return redirect(auth_url)

@auth_bp.route('/callback')
def ml_callback():
    code = request.args.get('code')
    token_url = 'https://api.mercadolibre.com/oauth/token'
    payload = {
        'grant_type': 'authorization_code',
        'client_id': current_app.config['ML_CLIENT_ID'],
        'client_secret': current_app.config['ML_CLIENT_SECRET'],
        'code': code,
        'redirect_uri': current_app.config['ML_REDIRECT_URI']
    }
    resp = post(token_url, data=payload).json()
    user = User.query.filter_by(username=str(resp.get('user_id'))).first()
    if not user:
        user = User(username=str(resp.get('user_id')))
    user.ml_access_token = resp.get('access_token')
    user.ml_refresh_token = resp.get('refresh_token')
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/logout')
@login_required
def ml_logout():
    logout_user()
    return redirect(url_for('main.index'))
```

## /app/routes.py  
**Modificado:** Sí (asegurar main_bp exportado)  
```python
from flask import Blueprint, jsonify, url_for
from flask_login import login_required, current_user
from rq import get_current_job
from app import db, redis_conn, task_queue
from app.tasks import fetch_store_stats

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return jsonify({'message': 'VelozML backend completo funcionando'})

@main_bp.route('/health')
def health():
    try:
        db.session.execute('SELECT 1')
        redis_conn.ping()
        return jsonify({'status': 'healthy'})
    except Exception as e:
        return jsonify({'status': 'error', 'detail': str(e)}), 500

@main_bp.route('/dashboard')
@login_required
def dashboard():
    job = task_queue.enqueue(fetch_store_stats, current_user.id)
    return jsonify({
        'job_id': job.get_id(),
        'status_url': url_for('main.task_status', job_id=job.get_id(), _external=True)
    })

@main_bp.route('/status/<job_id>')
@login_required
def task_status(job_id):
    job = get_current_job()
    return jsonify({
        'job_id': job_id,
        'status': job.get_status(),
        'result': job.result
    })
