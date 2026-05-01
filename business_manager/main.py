from fastapi import FastAPI
from routers import auth_router, employee_router

app = FastAPI()

app.include_router(auth_router.router, prefix="/auth")
app.include_router(employee_router.router, prefix="/employee")