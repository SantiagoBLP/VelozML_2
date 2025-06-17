from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import date
from app.models import MLAccount, Publication, Sale, Alert
from app import db

main_bp = Blueprint('main', __name__)  # url_prefix por defecto ''

@main_bp.route('/')
@login_required
def home():
    return redirect(url_for('main.dashboard'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    hoy = date.today()
    user_id = current_user.id
    # Ventas hoy
    ventas_hoy = Sale.query.join(MLAccount).filter(
        MLAccount.user_id == user_id,
        Sale.fecha >= hoy
    ).count()
    # Ventas este mes
    primer_dia_mes = hoy.replace(day=1)
    ventas_mes = Sale.query.join(MLAccount).filter(
        MLAccount.user_id == user_id,
        Sale.fecha >= primer_dia_mes
    ).count()
    # Preguntas pendientes (alertas no enviadas)
    pendientes = Alert.query.join(MLAccount).filter(
        MLAccount.user_id == user_id,
        Alert.tipo == 'preguntas_sin_responder',
        Alert.estado == 'no_enviada'
    ).count()
    # Reputación
    cuenta = MLAccount.query.filter_by(user_id=user_id).first()
    reputacion = cuenta.reputacion if cuenta else None
    return jsonify({
        'ventas_hoy': ventas_hoy,
        'ventas_mes': ventas_mes,
        'preguntas_pendientes': pendientes,
        'reputacion': reputacion
    })

@main_bp.route('/publicaciones')
@login_required
def publicaciones():
    user_id = current_user.id
    query = Publication.query.join(MLAccount).filter(MLAccount.user_id == user_id)
    estado = request.args.get('estado')
    if estado:
        query = query.filter(Publication.estado == estado)
    pubs = query.all()
    return jsonify([p.to_dict() for p in pubs])

@main_bp.route('/ventas')
@login_required
def ventas():
    user_id = current_user.id
    query = Sale.query.join(MLAccount).filter(MLAccount.user_id == user_id)
    estado = request.args.get('estado')
    if estado:
        query = query.filter(Sale.estado == estado)
    sales = query.all()
    return jsonify([s.to_dict() for s in sales])

@main_bp.route('/alertas')
@login_required
def alertas():
    user_id = current_user.id
    alerts = Alert.query.join(MLAccount).filter(MLAccount.user_id == user_id).all()
    return jsonify([a.to_dict() for a in alerts])
