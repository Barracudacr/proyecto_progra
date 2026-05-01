from pathlib import Path

#Ruta bae del proyecto
BASE_DIR = Path(__file__).resolve().parent

#Carpeta de datos
DATA_DIR = BASE_DIR / "data"

#URL del backend
API_BASE_URL = "http://127.0.0.1:8000"

#JWT
SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"