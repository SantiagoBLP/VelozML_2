import os
from datetime import datetime, timedelta
dimport requests
from app import db
from app.models import MLAccount, Publication, Sale, Alert

# --- Funciones de utilidades OAuth ML ---
def token_expirado(account: MLAccount) -> bool:
    # Asumimos que guardamos campo 'obtained_at' o similar; si ahora > obtained_at + expires_in
    # Para simplicidad: siempre refrescar antes de llamar a la API si expiración inminente
    return True  # implementar lógica real

def refresh_access_token(account: MLAccount):
    data = {
        'grant_type': 'refresh_token',
        'client_id': os.getenv('ML_CLIENT_ID'),
        'client_secret': os.getenv('ML_CLIENT_SECRET'),
        'refresh_token': account.get_refresh_token()
    }
    resp = requests.post('https://api.mercadolibre.com/oauth/token', data=data)
    tokens = resp.json()
    account.access_token = tokens['access_token']
    account.expires_in = tokens.get('expires_in', account.expires_in)
    account.set_refresh_token(tokens['refresh_token'])
    db.session.commit()

# --- Job diario de sincronización ---
def sync_daily():
    accounts = MLAccount.query.all()
    for acc in accounts:
        if token_expirado(acc):
            refresh_access_token(acc)
        # Publicaciones
        # [aquí invocar funciones de llamada a API ML]
        # Ventas
        # [similar]
        # Reputación
        # [similar]
    db.session.commit()

# --- Job de preguntas sin responder cada hora ---
def check_unanswered_questions():
    accounts = MLAccount.query.all()
    for acc in accounts:
        if token_expirado(acc):
            refresh_access_token(acc)
        resp = requests.get(
            f"https://api.mercadolibre.com/questions/search?seller_id={acc.ml_user_id}&status=UNANSWERED",
            headers={'Authorization': f'Bearer {acc.access_token}'}
        )
        total = resp.json().get('total', 0)
        alerta = Alert.query.filter_by(account_id=acc.id,
                                       tipo='preguntas_sin_responder',
                                       estado='no_enviada').first()
        if total > 0:
            mensaje = f"Tienes {total} preguntas sin responder"
            if alerta:
                alerta.mensaje = mensaje
                alerta.fecha = datetime.utcnow()
            else:
                db.session.add(Alert(account_id=acc.id,
                                     tipo='preguntas_sin_responder',
                                     mensaje=mensaje))
        else:
            if alerta:
                alerta.estado = 'enviada'
    db.session.commit()
