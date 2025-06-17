from dotenv import load_dotenv
import os

load_dotenv()  # carga variables de .env en desarrollo

from app import create_app, db

# Crear la aplicación
app = create_app()

# --- DEBUG: imprimir estructura de archivos para detectar la ubicación del WSGI app ---
print("📁 ROOT DIR:", os.listdir("."), flush=True)
if os.path.isdir("app"):
    for entry in os.listdir("app"):
        path = os.path.join("app", entry)
        if os.path.isdir(path):
            print(f"📂 app/{entry}:", os.listdir(path), flush=True)
        else:
            print(f"📄 app/{entry}", flush=True)
# -----------------------------------------------------------------------------------

if __name__ == '__main__':
    # Crear tablas si no existen (solo para dev)
    with app.app_context():
        db.create_all()
    # Correr con waitress en producción local o flask run en dev
    from waitress import serve
    serve(app, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
