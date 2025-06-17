from flask import Blueprint, redirect, request, session, url_for
from requests import get, post
from app import db, login
from app.models import User
from flask_login import login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@auth_bp.route('/login')
def ml_login():
    client_id = current_app.config['ML_CLIENT_ID']
    redirect_uri = current_app.config['ML_REDIRECT_URI']
    url = f"https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    return redirect(url)

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
    # Guardar o actualizar user
    user = User.query.filter_by(username=resp['user_id']).first() or User(username=str(resp['user_id']))
    user.ml_access_token = resp['access_token']
    user.ml_refresh_token = resp['refresh_token']
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

---

## 6. app/routes.py
```python
from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
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
    # Encolar tarea de stats asincrónica
    job = task_queue.enqueue(fetch_store_stats, current_user.id)
    return jsonify({'job_id': job.get_id()})
```  

---

## 7. app/tasks.py
```python
import requestsrom app import db
from app.models import StoreStat, User
def fetch_store_stats(user_id):
    user = User.query.get(user_id)
    headers = {'Authorization': f"Bearer {user.ml_access_token}"}
    sales = requests.get('https://api.mercadolibre.com/orders/search?seller='+user.username, headers=headers).json()
    total = sales.get('paging',{}).get('total',0)
    stat = StoreStat(user_id=user_id, total_sales=total)
    db.session.add(stat)
    db.session.commit()
