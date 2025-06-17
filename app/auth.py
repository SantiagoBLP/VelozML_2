from flask import Blueprint, redirect, request, url_for, current_app
from requests import post
from flask_login import login_user, logout_user, login_required

from app import db, login
from app.models import User

# Blueprint para autenticación con MercadoLibre
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Callback para cargar el usuario actual\@login.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@auth_bp.route('/login')
def ml_login():
    """
    Redirige al usuario al flujo OAuth de MercadoLibre.
    """
    client_id = current_app.config['ML_CLIENT_ID']
    redirect_uri = current_app.config['ML_REDIRECT_URI']
    auth_url = (
        f"https://auth.mercadolibre.com.ar/authorization"
        f"?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
    )
    return redirect(auth_url)

@auth_bp.route('/callback')
def ml_callback():
    """
    Recibe el código de autorización, intercambia tokens, crea/actualiza el usuario y lo loguea.
    """
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

    # Obtener o crear el usuario
    user = User.query.filter_by(username=str(resp.get('user_id'))).first()
    if not user:
        user = User(username=str(resp.get('user_id')))

    # Almacenar tokens
    user.ml_access_token = resp.get('access_token')
    user.ml_refresh_token = resp.get('refresh_token')

    db.session.add(user)
    db.session.commit()

    # Iniciar sesión del usuario
    login_user(user)
    return redirect(url_for('main.dashboard'))

@auth_bp.route('/logout')
@login_required
def ml_logout():
    """
    Cierra la sesión del usuario.
    """
    logout_user()
    return redirect(url_for('main.index'))
