from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.auth import register_company, login_company

router = APIRouter()

#modelo para registro
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    

#modelo para login
class LoginRequest(BaseModel):
    email: str
    password: str


#endpoint: Register
@router.post("/register")
def register(data: RegisterRequest):
    company = register_company(data.name,data.email,data.password)
    
    if not company:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    return {"message": "Empresa registrada", "company_id": company}


#endpoint: Login
@router.post("/login")
def login(data: LoginRequest):
    token = login_company(data.email,data.password)
    
    if not token:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    return{"access_token": token, "token_type": "bearer"}