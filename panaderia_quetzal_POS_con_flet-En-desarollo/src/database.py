import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

from contextlib import contextmanager
import sys
import os
sys.path.append(os.path.dirname(__file__))
from session_state import get_session

from pathlib import Path

# Configurar la ruta al archivo .env (está un nivel arriba de 'src')
env_path = Path(__file__).resolve().parent.parent / '.env'

if env_path.exists():
    print(f"✅ Archivo .env encontrado en: {env_path}")
    load_dotenv(dotenv_path=env_path)
    print(f"📡 Intentando conectar a HOST: {os.getenv('DB_HOST')}")
else:
    print(f"❌ ERROR: No se encontró el archivo .env en: {env_path}")
    # Intentar carga normal como fallback
    load_dotenv()

@contextmanager
def get_db_connection():
    """
    Context manager para manejar las conexiones a la base de datos de manera dinámica por RBAC.
    """
    conexion = None
    sesion = get_session()
    
    # Prioridad: 1. Sesion del usuario actual, 2. Variable de entorno como fallback
    db_user = sesion.current_user if sesion.current_user else os.getenv("DB_USER", "root")
    db_pass = sesion.current_password if sesion.current_password else os.getenv("DB_PASSWORD", "")
    
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=db_user,
            password=db_pass,
            database=os.getenv("DB_NAME", "panaderia"),
            connect_timeout=3
        )
        yield conexion
    except Error as e:
        # Errores de red típicos: 2002 (Connection refused), 2003 (Can't connect), 2006 (Server gone), 2013 (Lost connection)
        if e.errno in (2002, 2003, 2006, 2013):
            print(f"Error de red al servidor principal ({e}). Intentando con la réplica...")
            try:
                conexion = mysql.connector.connect(
                    host=os.getenv("DB_HOST_REPLICA", "10.0.0.2"),
                    user=db_user,
                    password=db_pass,
                    database=os.getenv("DB_NAME", "panaderia"),
                    connect_timeout=3
                )
                print("¡Conectado al servidor de réplica exitosamente!")
                yield conexion
            except Error as replica_error:
                print(f"Error crítico: Ambos servidores de base de datos están caídos. ({replica_error})")
                raise replica_error
        else:
            # Es un error de permisos o sintaxis (ej. 1142), no de conexión
            raise e
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass