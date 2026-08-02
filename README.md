
# UAgenda

Una aplicación diseñada en Ingeniería de Software, y refinado en Arquitectura de Software. Su propósito es ser un HUB estudiantil en el que el estudiante pueda gestionar sus cuestiones de organización académica.


## Autores

- Valery Martinez Posner
- Carol Juliana Ariza Triana
- Iván Felipe Ayala Rengifo


## Instalación

Para el commit actual, la base de datos no se encuentra en deploy, por lo que las siguientes instrucciones ayudarán a ejecutar el proyecto de manera local e igualmente funcional.

1. Asegurarse de tener instalada la versión más reciente de Python o, en su defecto, alguna versión superior a Python 3.9
2. En la carpeta del repositorio, ejecutar el siguiente comando:

```bash
  python -m pip install -r requirements.txt
```
Esto instalará las dependencias necesarias.

3. Instalar MySQL y MySQL Workbench, y crear las credenciales para un usuario root, con nombre de usuario y contraseña.
4. En MySQL Workbench, se deberá crear un nuevo SCHEMA llamado prflask, y se deberá cargar el archivo *prflask_local.sql* que se encuentra en la raíz del proyecto. Al ejecutarlo en el SCHEMA recién creado, se creará la base de datos completa.

4. En main.py, se encuentra el siguiente fragmento de código:

```python
    # Cargar variables de entorno para las credenciales
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD_UNAGENDA")
    EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD_UNAGENDA")

    # Crear una instancia de la aplicación Flask
    app = Flask(__name__, template_folder="templates")

    # Configuración de la conexión a la base de datos MySQL (local)
    app.config["MYSQL_HOST"] = "localhost"
    app.config["MYSQL_USER"] = "root"
    app.config["MYSQL_PASSWORD"] = MYSQL_PASSWORD
    app.config["MYSQL_DB"] = "prflask"
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"
```

Por el momento, para la instalación local, es importante declarar las variables de entorno para que hagan match con el usuario root.

```powershell
[Environment]::SetEnvironmentVariable("MYSQL_PASSWORD_UNAGENDA", "Contraseña seteada para el usuario root durante la instalación de MySQL.", "User")
```
```powershell
[Environment]::SetEnvironmentVariable("EMAIL_PASSWORD_UNAGENDA", "usuario1@example.com", "User")
```

Una vez hecho todo lo anterior, simplemente en el directorio raíz del proyecto ejecutar:
```python
python main.py
```

El proyecto se ejecutará en el directorio indicado en la terminal de Python de manera local.