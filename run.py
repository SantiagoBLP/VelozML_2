import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Crear tablas en desarrollo
    with app.app_context():
        from app.models import db
        db.create_all()
    # Servir con Waitress en local o Render con gunicorn
    from waitress import serve
    serve(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
