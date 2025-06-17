import os
from flask import Blueprint, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
import requests
from app import db
from app.models import User, MLAccount

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --------------------------------------------------
# Rutas de registro/login local (opcional)
# --------------------------------------------------

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Lógica de formulario para registrar un usuario local
    # Al crear: user.set_password(password), db.session.add(user), db.session.commit()
    pass

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Lógica de login: verificar email/pass y login_user(user)
    pass

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))

# --------------------------------------------------
# OAuth con MercadoLibre
# --------------------------------------------------

@auth_bp.route('/login_ml')
@login_required
def ml_login():
    """
    Redirige al usuario al flujo de OAuth de MercadoLibre.
    """
    state = os.urandom(16).hex()
    # Guardar state en sesión
    session['ml_oauth_state'] = state
    auth_url = (
        f"https://auth.mercadolibre.com.ar/authorization"
        f"?response_type=code"
        f"&client_id={os.getenv('ML_CLIENT_ID')}"
        f"&redirect_uri={os.getenv('ML_REDIRECT_URI')}"
        f"&state={state}"
    )
    return redirect(auth_url)

@auth_bp.route('/callback')
def ml_callback():
    error = request.args.get('error')
    if error:
        flash('Error de autorización con MercadoLibre.', 'danger')
        return redirect(url_for('main.dashboard'))
    code = request.args.get('code')
    state = request.args.get('state')
    # Validar state
    if state != session.get('ml_oauth_state'):
        flash('State inválido. Intenta de nuevo.', 'danger')
        return redirect(url_for('main.dashboard'))
    # Intercambio de código por tokens
    data = {
        'grant_type': 'authorization_code',
        'client_id': os.getenv('ML_CLIENT_ID'),
        'client_secret': os.getenv('ML_CLIENT_SECRET'),
        'code': code,
        'redirect_uri': os.getenv('ML_REDIRECT_URI')
    }
    token_resp = requests.post('https://api.mercadolibre.com/oauth/token', data=data)
    resp_data = token_resp.json()
    # Extraer tokens y datos
    access_token  = resp_data.get('access_token')
    refresh_token = resp_data.get('refresh_token')
    expires_in    = resp_data.get('expires_in')
    ml_user_id    = resp_data.get('user_id')
    # Obtener datos de la cuenta ML (nickname, site_id)
    user_info = requests.get(f'https://api.mercadolibre.com/users/{ml_user_id}',
                              headers={'Authorization': f'Bearer {access_token}'}).json()
    nickname = user_info.get('nickname')
    site_id  = user_info.get('site_id')
    # Guardar en BD
    ml_acc = MLAccount(
        user_id=current_user.id,
        ml_user_id=ml_user_id,
        access_token=access_token,
        expires_in=expires_in,
        site_id=site_id,
        nickname=nickname
    )
    ml_acc.set_refresh_token(refresh_token)
    db.session.add(ml_acc)
    db.session.commit()
    flash('Cuenta de MercadoLibre vinculada.', 'success')
    return redirect(url_for('main.dashboard'))
