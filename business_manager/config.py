from pathlib import Path

#Ruta bae del proyecto
BASE_DIR = Path(__file__).resolve().parent

#Carpeta de datos
DATA_DIR = BASE_DIR / "data"

#URL del backend
API_BASE_URL = "http://127.0.0.1:8000"

#JWT
SECRET_KEY = "mi_clave_super_segura_de_32_caracteres_123"
ALGORITHM = "HS256"