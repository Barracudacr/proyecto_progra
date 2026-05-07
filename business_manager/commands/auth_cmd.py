import typer
import httpx
from utils.auth import save_token,clear_token
from config import API_BASE_URL
from rich.console import Console


app = typer.Typer()
console = Console()


@app.command("register")
def register():
    name = typer.prompt("Nombre de la empresa")
    email = typer.prompt("Email de la empresa")
    password = typer.prompt("Contraseña de la empresa",hide_input=True)
    
    response = httpx.post(
        f"{API_BASE_URL}/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password
        }
    )
    
    if response.status_code != 200:
        console.print("[red]Error al registrar las empresa[/red]")
        console.print("response.text")
        return
    
    console.print("[green]Empresa registrada correctamente[/green]")

@app.command("login")
def login():
    email = typer.prompt("Email")
    password = typer.prompt("Contraseña",hide_input=True)
    
    response = httpx.post(
        f"{API_BASE_URL}/auth/login",
        json={"email":email,"password": password}
    )
    
    if response.status_code != 200:
        console.print("[red]Error al tratar de loguearse[/red]")
        console.print(response.text)
        return

    token = response.json()["access_token"]
    save_token(token)
    
    console.print("[green]Login exitoso[/green]")


@app.command("logout")
def logout():
    clear_token()
    console.print("[green]Sesión cerrada[/green]")
