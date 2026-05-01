import hashlib
import jwt
from datetime import datetime, timedelta,timezone
from core.data_manager import read_data, write_data
from config import SECRET_KEY, ALGORITHM


def hash_password(password: str)-> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_token(company_id: str):
    payload = {
        "company_id": company_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token:str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        print("Token expirado")
        return None
    except jwt.InvalidTokenError:
        print("Token inválido")
        return None
    except Exception as e:
        print("Error inesperado:",e)
        return None


def register_company(name: str, email: str, password: str):
    companies = read_data("companies.json")
    
    
    #verificar si ya existe la empresa
    for c in companies:
        if c["email"] == email:
            return None, "Email ya registrado"
    
    new_company = {
        "id": f"comp_{len(companies) + 1}",
        "name": name,
        "email": email,
        "password": hash_password(password),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True
    }
    
    
    companies.append(new_company)
    write_data("companies.json", companies)
    
    return new_company


def login_company(email: str, password: str):
    companies = read_data("companies.json")
    hashed = hash_password(password)
    
    for c in companies:
        if c["email"] == email and c["password"] == hashed:
            token = create_token(c["id"])
            return token
        
    return None