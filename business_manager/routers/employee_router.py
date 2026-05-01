from fastapi import APIRouter, Depends,HTTPException
from core.security import get_current_company
from core.data_manager import read_data, write_data
from models.employee import EmployeeCreate, EmployeeUpdate
from uuid import uuid4


router = APIRouter()


#helper para archivo por empresa
def get_company_file(company_id: str):
    return f"employees_{company_id}.json"


#Create
@router.post("/")
def create_employee(data: EmployeeCreate, current=Depends(get_current_company)):
    filename = get_company_file(current["company_id"])
    employees = read_data(filename)
    
    new_employee = data.dict()
    new_employee["id"] = str(uuid4())
    new_employee["status"] = "active"
    
    employees.append(new_employee)
    write_data(filename,employees)
    
    return new_employee


#Read(todos)
@router.get("/")
def get_employees(current=Depends(get_current_company)):
    filename = get_company_file(current["company_id"])
    return read_data(filename)


#Read(uno)
@router.get("/{employee_id}")
def get_employee(employee_id: str,current=Depends(get_current_company)):
    filename = get_company_file(current["company_id"])
    employees = read_data(filename)
    
    for emp in employees:
        if emp["id"] == employee_id:
            return emp
    
    raise HTTPException(status_code=404, detail="Empleado no encontrado")


#Update
@router.put("/{employee_id}")
def update_employee(employee_id: str, data: EmployeeUpdate, current=Depends(get_current_company)):
    filename = get_company_file(current["company_id"])
    employees = read_data(filename)
    
    for i,emp in enumerate(employees):
        if emp["id"] == employee_id:
            updated = data.dict(exclude_unset=True)
            
            employees[i].update(updated)
            write_data(filename,employees)
            
            return employees[i]
    
    raise HTTPException(status_code=404, detail="Empleado no encontrado")


#Delete
@router.delete("/{employee_id}")
def delete_employee(employee_id: str,current=Depends(get_current_company)):
    filename = get_company_file(current["company_id"])
    employees = read_data(filename)
    
    new_employees = [emp for emp in employees if emp["id"] != employee_id]
    
    write_data(filename,new_employees)
    
    return {"message": "Empleado eliminado"}