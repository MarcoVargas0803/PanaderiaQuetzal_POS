import mysql.connector
from database import get_db_connection
import json

def limpiar_cursor(cursor):
    """Asegura que todos los resultados de un procedimiento sean consumidos."""
    try:
        while cursor.nextset():
            pass
    except:
        pass

def obtener_productos_por_categoria(categoria_nombre):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vista_productos_disponibles WHERE categoria = %s", (categoria_nombre,))
        return cursor.fetchall()

def registrar_venta_directa(usuario_id, caja_id, total, detalles, metodo_pago):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        detalles_json = json.dumps(detalles)
        cursor.callproc("sp_RegistrarVentaDirectaDetallada", (usuario_id, caja_id, total, detalles_json, metodo_pago))
        limpiar_cursor(cursor)
        conn.commit()

def registrar_apartado_detallado(usuario_id, caja_id, cliente_id, fecha_entrega, anticipo, total, detalles, metodo_pago="Efectivo"):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        detalles_json = json.dumps(detalles)
        args = (cliente_id, usuario_id, caja_id, total, anticipo, detalles_json, fecha_entrega, metodo_pago)
        cursor.callproc("sp_CrearApartadoDetallado", args)
        limpiar_cursor(cursor)
        conn.commit()

def obtener_caja_activa(usuario_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT cajas_id FROM cajas WHERE usuarios_id = %s AND fecha_cierre IS NULL LIMIT 1", (usuario_id,))
            res = cursor.fetchone()
            if res:
                return res['cajas_id']
    except Exception as e:
        print(f"Error consultando caja activa (posible falta de permisos): {e}")
    return None

def abrir_caja(usuario_id, saldo_inicial):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.callproc("sp_AbrirCaja", (usuario_id, saldo_inicial))
        limpiar_cursor(cursor)
        conn.commit()

def cerrar_caja(caja_id, saldo_final):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.callproc("sp_CerrarCaja", (caja_id, saldo_final))
        limpiar_cursor(cursor)
        conn.commit()

def obtener_corte_caja(caja_id):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vista_corte_caja WHERE cajas_id = %s", (caja_id,))
        return cursor.fetchone()

def registrar_cliente(nombre, telefono):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nombre, telefono) VALUES (%s, %s)", (nombre, telefono))
        conn.commit()

def obtener_clientes():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT clientes_id, nombre FROM clientes ORDER BY nombre")
        return cursor.fetchall()

def obtener_historial_ventas(limite=50):
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        # Consultamos las tablas directamente para tener folios individuales (no agrupados por día)
        query = """
            SELECT 
                v.ventas_id AS folio,
                v.fecha,
                u.nombre AS cajero,
                p.nombre AS producto,
                dv.cantidad,
                CAST(dv.precio_historico AS FLOAT) AS precio,
                CAST((dv.cantidad * dv.precio_historico) AS FLOAT) AS subtotal,
                v.es_apartado
            FROM ventas v
            JOIN detalle_venta dv ON v.ventas_id = dv.ventas_id
            JOIN productos p ON dv.productos_id = p.productos_id
            JOIN usuarios u ON v.usuarios_id = u.usuarios_id
            WHERE v.cancelada = 0
            ORDER BY v.fecha DESC
            LIMIT %s
        """
        cursor.execute(query, (limite,))
        return cursor.fetchall()

def obtener_resumen_dashboard():
    resumen = {
        "ingresos_hoy": 0.0,
        "ventas_directas": 0,
        "apartados_creados": 0,
        "unidades_mermadas": 0,
        "productos_estrella": [],
        "inventario_critico": [],
        "rentabilidad": [],
        "balance": []
    }
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        # 1. Resumen del día
        cursor.execute("SELECT * FROM vista_resumen_dia LIMIT 1")
        row = cursor.fetchone()
        if row:
            resumen["ventas_directas"] = row.get("ventas_directas") or 0
            resumen["ingresos_hoy"] = float(row.get("ingresos_ventas") or 0) + float(row.get("anticipos_cobrados") or 0)
            resumen["apartados_creados"] = row.get("apartados_creados") or 0
            resumen["unidades_mermadas"] = row.get("unidades_merma") or 0
            
        # Saldo pendiente total (Lo que nos deben los clientes)
        cursor.execute("SELECT CAST(SUM(saldo_pendiente) AS FLOAT) as pendiente FROM vista_saldos_apartados")
        resumen["total_pendiente"] = cursor.fetchone().get("pendiente") or 0.0
        
        # 2. Productos estrella (Casting a float)
        cursor.execute("SELECT producto, unidades_vendidas, CAST(porcentaje_ventas AS FLOAT) as porcentaje_ventas FROM vista_productos_estrella LIMIT 5")
        resumen["productos_estrella"] = cursor.fetchall()
        
        # 3. Inventario Crítico
        cursor.execute("SELECT producto, stock FROM vista_inventario_critico LIMIT 10")
        resumen["inventario_critico"] = cursor.fetchall()

        # 4. Métricas avanzadas (Casting a float)
        try:
            cursor.execute("SELECT producto, CAST(rentabilidad_neta AS FLOAT) as rentabilidad_neta FROM vista_rentabilidad_productos LIMIT 5")
            resumen["rentabilidad"] = cursor.fetchall()
            
            cursor.execute("SELECT producto, CAST(unidades_producidas AS FLOAT) as unidades_producidas, CAST(unidades_vendidas AS FLOAT) as unidades_vendidas, CAST(unidades_merma AS FLOAT) as unidades_merma FROM vista_balance_produccion LIMIT 5")
            resumen["balance"] = cursor.fetchall()
        except Exception as e: 
            print(f"Error en métricas: {e}")
    return resumen

def obtener_saldos_apartados():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vista_saldos_apartados ORDER BY saldo_pendiente DESC LIMIT 20")
        return cursor.fetchall()

def obtener_proximas_entregas():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        # Mostrar entregas de hoy y mañana para que siempre haya info útil
        cursor.execute("SELECT * FROM vista_entregas_semana WHERE fecha_entrega <= DATE_ADD(CURDATE(), INTERVAL 1 DAY)")
        return cursor.fetchall()

def obtener_productos_caducar():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        # Aumentar a 7 días para que sea preventivo
        cursor.execute("SELECT * FROM vista_productos_proximos_caducar WHERE dias_restantes <= 7")
        return cursor.fetchall()

def registrar_produccion(usuario_id, producto_id, cantidad):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.callproc("sp_RegistrarProduccion", (usuario_id, producto_id, cantidad))
        limpiar_cursor(cursor)
        conn.commit()

def registrar_merma(usuario_id, producto_id, cantidad):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.callproc("sp_RegistrarMerma", (usuario_id, producto_id, cantidad))
        limpiar_cursor(cursor)
        conn.commit()
