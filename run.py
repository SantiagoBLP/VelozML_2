import os
from dotenv import load_dotenv
load_dotenv()  # carga .env en desarrollo
from app import create_app, db
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    from waitress import serve
    serve(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
