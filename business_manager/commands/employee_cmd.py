import typer
import httpx
from rich.console import Console
from rich.table import Table
from utils.token import get_token

app = typer.Typer()
console = Console()

BASE_URL = "http://127.0.0.1:8000"


@app.command("list")
def list_employees():
    token = get_token()
    
    if not token:
        console.print("[red]No estás logueado[/red]")
        return
    
    response = httpx.get(
        f"{BASE_URL}/employee/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 200:
        console.print("[red]Error al obtener empleados[/red]")
        return
    
    employees = response.json()
    
    
    table = Table(title="Empleados")
    
    table.add_column("ID")
    table.add_column("Nombre")
    table.add_column("Cargo")
    table.add_column("Departamento")
    table.add_column("Salario")
    table.add_column("Fecha de contratación")
    
    for emp in employees:
        table.add_row(
            str(emp["id"]),
            f"{emp['first_name']} {emp['last_name']}",
            str(emp["position"]),
            str(emp["department"]),
            str(f"${emp["salary"]}"),
            str(emp["hire_date"])
        )
    
    console.print(table)


@app.command("create")
def create_employee():
    token = get_token()
    
    if not token:
        console.print("[red]No estás logueado[/red]")
        return
    
    
    #pedir datos
    first_name = typer.prompt("Nombre")
    last_name = typer.prompt("Apellido")
    email = typer.prompt("Email")
    position = typer.prompt("Cargo")
    department = typer.prompt("Departamento")
    salary = typer.prompt("Salario",type=float)
    
    
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "position": position,
        "department": department,
        "salary": salary,
        
    }
    
    response = httpx.post(
        f"{BASE_URL}/employee/",
        json=data,
        headers={"Authorization":f"bearer {token}"}
    )
    
    if response.status_code != 200:
        console.print("[red]Error al crear empleado[/red]")
        console.print(response.text)
        return
    
    console.print("[green]Empleado creado correctamente[/green]")