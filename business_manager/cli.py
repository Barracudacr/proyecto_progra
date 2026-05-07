import typer
import sys
from commands import employee_cmd,auth_cmd
from utils.auth import get_token,clear_token


app = typer.Typer()



#limpiar pantalla
def clear_screen():
    print("\033c", end="")
    
#pausa
def pause():
    input("\nPresiona ENTER para continuar...")

#Menú

def main_menu():
    while True:
        pause()
        clear_screen()
        print("\n===Mneú Principal===")
        print("1. Registrar empresa")
        print("2. Login")
        print("3. Salir")    
        
        option = input("Seleccione una opción: ")
        
        if option == "1":
            auth_cmd.register()
        elif option == "2":
            auth_cmd.login()
            
            #login correcto
            if get_token():
                employee_menu()
            else:
                print("Login fallido")
        elif option == "3":
            print("Saliendo...")
            sys.exit()
        else:
            print("Opción inválida")



#Menú Empleados

def employee_menu():
    while True:
        pause()
        clear_screen()
        print("\n===Bienvenido===")
        print("1. Listar empleados")
        print("2. Crear empleado")
        print("3. Editar empleado")
        print("4. Eliminar empleado")
        print("5. Logout")

        option = input("Seleccione una opción: ")
        
        if option == "1":
            employee_cmd.list_employees()
        elif option == "2":
            employee_cmd.create_employee()
        elif option == "3":
            employee_cmd.update_employee()
        elif option == "4":
            employee_cmd.delete_empployee()
        elif option == "5":
            auth_cmd.logout()
            clear_token()
            main_menu()
        else:
            print("Opción invalida")



@app.command()
def start():
    """
    Inicia modo interactivo
    """
    clear_token()
    main_menu()



app.add_typer(employee_cmd.app,name="employees")
app.add_typer(auth_cmd.app,name="auth")


app.command()(auth_cmd.login)
app.command()(auth_cmd.logout)
app.command()(auth_cmd.register)


if __name__ == "__main__":
    app()