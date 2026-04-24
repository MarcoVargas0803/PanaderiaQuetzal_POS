import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

from contextlib import contextmanager
import sys
import os
sys.path.append(os.path.dirname(__file__))
from session_state import get_session

# Esto busca el archivo .env en la raíz del proyecto
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
            database=os.getenv("DB_NAME", "panaderia")
        )
        yield conexion
    except Error as e:
        print(f"Error en la base de datos MySQL ({db_user}): {e}")
        raise e
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass