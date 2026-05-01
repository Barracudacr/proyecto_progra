from fastapi import Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from core.auth import verify_token

security = HTTPBearer()


def get_current_company(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401,detail="Token inválido o expirado")
    
    return payload 