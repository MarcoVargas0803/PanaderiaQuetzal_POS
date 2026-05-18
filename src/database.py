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

def create_raw_connection(db_user, db_pass):
    """
    Crea una conexión con la lógica de verificación de read_only y failover.
    Retorna: (conexion, es_replica, es_read_only)
    """
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=db_user,
            password=db_pass,
            database=os.getenv("DB_NAME", "panaderia"),
            connect_timeout=3
        )
        
        # Verificar estado read_only del Maestro
        cursor = conn.cursor()
        cursor.execute("SELECT @@global.read_only;")
        ro = cursor.fetchone()[0]
        cursor.close()
        
        if ro == 1:
            conn.close()
            # El maestro está en read_only (probablemente en mantenimiento o hubo un split-brain)
            # Lanzamos error para forzar el failover
            raise Error(msg="El Maestro está en modo Solo Lectura (read_only=ON).", errno=2003)
            
        return conn, False, False

    except Error as e:
        # Errores de red típicos o error forzado por read_only
        if getattr(e, 'errno', 0) in (2002, 2003, 2006, 2013) or "Solo Lectura" in str(e):
            print(f"Fallo Maestro ({e}). Intentando con la réplica...")
            try:
                conn_replica = mysql.connector.connect(
                    host=os.getenv("DB_HOST_REPLICA", "10.0.0.2"),
                    user=db_user,
                    password=db_pass,
                    database=os.getenv("DB_NAME", "panaderia"),
                    connect_timeout=3
                )
                
                # Verificar estado read_only del Esclavo
                cursor = conn_replica.cursor()
                cursor.execute("SELECT @@global.read_only;")
                ro = cursor.fetchone()[0]
                cursor.close()
                
                print(f"¡Conectado al servidor de réplica exitosamente! read_only={ro}")
                return conn_replica, True, bool(ro)
            except Error as replica_error:
                print(f"Error crítico: Ambos servidores de base de datos están inaccesibles. ({replica_error})")
                raise replica_error
        else:
            # Es un error de permisos (ej. 1142) o autenticación, no de conexión
            raise e

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
        conexion, is_replica, is_ro = create_raw_connection(db_user, db_pass)
        sesion.is_read_only = is_ro
        sesion.is_replica = is_replica
        yield conexion
    finally:
        if conexion:
            try:
                conexion.close()
            except:
                pass