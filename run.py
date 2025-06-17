import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Creación de tablas (solo en dev)
    with app.app_context():
        from app.models import db
        db.create_all()
    # Ejecutar con Waitress
    from waitress import serve
    serve(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
