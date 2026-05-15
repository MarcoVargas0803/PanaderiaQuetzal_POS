import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="panadero_quetzal",
        password="Panadero@Quetzal2026",
        database="panaderia"
    )
    cursor = conn.cursor()
    print("Conexion exitosa como panadero_quetzal")
    cursor.callproc("sp_RegistrarProduccion", (3, 1, 5))
    conn.commit()
    print("sp_RegistrarProduccion ejecutado exitosamente!")
except Error as e:
    print(f"Error MySQL: {e}")
except Exception as e:
    print(f"Otro error: {e}")
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
