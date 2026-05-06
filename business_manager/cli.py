import typer
from commands import employee_cmd

app = typer.Typer()


app.add_typer(employee_cmd.app,name="employees")

if __name__ == "__main__":
    app()