from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Optional


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_lenght=2, max_length=50)
    email: EmailStr
    position: str
    department: str
    salary: float = Field(...,gt=0)
    hire_date:date
    

class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    position: Optional[str] = None
    department: Optional[str] = None
    salary: Optional[float] = Field(None,gt=0)
    hire_date: Optional[date] = None


class EmployeeResponse(EmployeeBase):
    id: str
    status: str