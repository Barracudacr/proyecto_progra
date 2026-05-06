from core.data_manager import read_data,write_data
from fastapi import HTTPException
from uuid import uuid4

#helper para archivo por empresa
def get_company_file(company_id: str):
    return f"employees_{company_id}.json"


#CREATE
def create_employee_service(data,company_id):
    filename = get_company_file(company_id)
    employees = read_data(filename)
    
    new_employee = data.model_dump()
    new_employee["id"] = str(uuid4())
    new_employee["status"] = "active"
    new_employee["hire_date"] = str(new_employee["hire_date"])
    
    employees.append(new_employee)
    write_data(filename,employees)
    
    return new_employee


#READ ALL
def get_all_employees_service(company_id):
    filename = get_company_file(company_id)
    return read_data(filename)


#READ ONE
def get_employee_service(employee_id,company_id):
    filename = get_company_file(company_id)
    employees = read_data(filename)
    
    for emp in employees:
        if emp["id"] == employee_id:
            return emp
    
    raise HTTPException(status_code=404, detail="Empleado no encontrado")


#UPDATE
def update_employee_service(employee_id,data,company_id):
    filename = get_company_file(company_id)
    employees = read_data(filename)
    
    for i,emp in enumerate(employees):
        if emp["id"] == employee_id:
            updated = data.model_dump(exclude_unset=True)
            
            if "hire_date" in updated:
                updated["hire_date"] = str(updated["hire_date"])
                
            employees[i].update(updated)
            write_data(filename,employees)
            
            return employees[i]
    
    raise HTTPException(status_code=404,detail="Empleado no encontrado")


#DELETE
def delete_employee_service(employee_id,company_id):
    filename = get_company_file(company_id)
    employees = read_data(filename)
    
    for i,emp in enumerate(employees):
        if emp["id"] == employee_id:
            employees.pop(i)
            write_data(filename,employees)
            return{"message":"Empleado eliminado"}
    
    raise HTTPException(status_code=404,detail="Empleado no encontrado")
