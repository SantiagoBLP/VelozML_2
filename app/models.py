import os
from datetime import datetime
tly import db
from flask_login import UserMixin
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash

# Clave de cifrado para refresh tokens
fernet = Fernet(os.getenv('ENCRYPTION_KEY').encode())

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id             = db.Column(db.Integer, primary_key=True)
    email          = db.Column(db.String(255), unique=True, nullable=False)
    password_hash  = db.Column(db.String(128), nullable=False)
    plan           = db.Column(db.String(20), default='free')
    fecha_alta     = db.Column(db.DateTime, default=datetime.utcnow)
    accounts       = db.relationship('MLAccount', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class MLAccount(db.Model):
    __tablename__ = 'ml_accounts'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ml_user_id       = db.Column(db.String(50), nullable=False)  # ID de ML
    access_token     = db.Column(db.String(255), nullable=False)
    refresh_token_enc = db.Column(db.LargeBinary, nullable=False)
    expires_in       = db.Column(db.Integer)
    site_id          = db.Column(db.String(5))
    nickname         = db.Column(db.String(100))
    reputacion       = db.Column(db.String(50))

    user             = db.relationship('User', back_populates='accounts')
    publicaciones    = db.relationship('Publication', back_populates='account')
    ventas           = db.relationship('Sale', back_populates='account')
    alertas          = db.relationship('Alert', back_populates='account')

    def set_refresh_token(self, token_str):
        self.refresh_token_enc = fernet.encrypt(token_str.encode())

    def get_refresh_token(self):
        return fernet.decrypt(self.refresh_token_enc).decode()

class Publication(db.Model):
    __tablename__ = 'publicaciones'
    id                   = db.Column(db.Integer, primary_key=True)
    account_id           = db.Column(db.Integer, db.ForeignKey('ml_accounts.id'), nullable=False)
    id_ml                = db.Column(db.String(50), nullable=False)
    titulo               = db.Column(db.String(300))
    estado               = db.Column(db.String(50))
    visitas              = db.Column(db.Integer)
    ventas               = db.Column(db.Integer)
    stock                = db.Column(db.Integer)
    precio               = db.Column(db.Float)
    categoria            = db.Column(db.String(100))
    reputacion_publicacion = db.Column(db.String(50))
    fecha_actualizacion  = db.Column(db.DateTime)

    account              = db.relationship('MLAccount', back_populates='publicaciones')

    def to_dict(self):
        return {
            'id_ml': self.id_ml,
            'titulo': self.titulo,
            'estado': self.estado,
            'visitas': self.visitas,
            'ventas': self.ventas,
            'stock': self.stock,
            'precio': self.precio,
            'categoria': self.categoria,
            'reputacion_publicacion': self.reputacion_publicacion,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }

class Sale(db.Model):
    __tablename__ = 'ventas'
    id              = db.Column(db.Integer, primary_key=True)
    account_id      = db.Column(db.Integer, db.ForeignKey('ml_accounts.id'), nullable=False)
    ml_sale_id      = db.Column(db.String(50), unique=True, nullable=False)
    producto        = db.Column(db.String(255))
    monto           = db.Column(db.Float)
    fecha           = db.Column(db.DateTime)
    estado          = db.Column(db.String(50))

    account         = db.relationship('MLAccount', back_populates='ventas')

    def to_dict(self):
        return {
            'ml_sale_id': self.ml_sale_id,
            'producto': self.producto,
            'monto': self.monto,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'estado': self.estado
        }

class Alert(db.Model):
    __tablename__ = 'alertas'
    id          = db.Column(db.Integer, primary_key=True)
    account_id  = db.Column(db.Integer, db.ForeignKey('ml_accounts.id'), nullable=False)
    tipo        = db.Column(db.String(50))
    mensaje     = db.Column(db.String(255))
    fecha       = db.Column(db.DateTime, default=datetime.utcnow)
    estado      = db.Column(db.String(20), default='no_enviada')

    account     = db.relationship('MLAccount', back_populates='alertas')

    def to_dict(self):
        return {
            'tipo': self.tipo,
            'mensaje': self.mensaje,
            'fecha': self.fecha.isoformat(),
            'estado': self.estado
        }
