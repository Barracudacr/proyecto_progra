from fastapi import APIRouter, Depends
from core.security import get_current_company
from models.employee import EmployeeCreate, EmployeeUpdate
from services.employee_service import(
    create_employee_service,
    get_all_employees_service,
    get_employee_service,
    update_employee_service,
    delete_employee_service
)


router = APIRouter()


#Create
@router.post("/")
def create_employee(data: EmployeeCreate, current=Depends(get_current_company)):
    return create_employee_service(data,current["company_id"])


#Read(todos)
@router.get("/")
def get_employees(current=Depends(get_current_company)):
    return get_all_employees_service(current["company_id"])


#Read(uno)
@router.get("/{employee_id}")
def get_employee(employee_id: str,current=Depends(get_current_company)):
    return get_employee_service(employee_id,current["company_id"])


#Update
@router.put("/{employee_id}")
def update_employee(employee_id: str, data: EmployeeUpdate, current=Depends(get_current_company)):
    return update_employee_service(employee_id,data,current["company_id"])

#Delete
@router.delete("/{employee_id}")
def delete_employee(employee_id: str,current=Depends(get_current_company)):
    return delete_employee_service(employee_id,current["company_id"])