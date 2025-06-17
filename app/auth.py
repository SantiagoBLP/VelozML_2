from flask import Blueprint, redirect, request, session, url_for, current_app
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
    url = (
        f"https://auth.mercadolibre.com.ar/authorization"
        f"?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    )
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
    user = User.query.filter_by(username=str(resp['user_id'])).first()
    if not user:
        user = User(username=str(resp['user_id']))
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
