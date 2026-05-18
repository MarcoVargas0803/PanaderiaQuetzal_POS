USE `panaderia`;

DELIMITER $$

-- 1. Procedimiento Almacenado para Liquidar un Apartado
DROP PROCEDURE IF EXISTS `sp_LiquidarApartado`$$
CREATE PROCEDURE `sp_LiquidarApartado`(
    IN p_apartado_id INT,
    IN p_caja_id INT,
    IN p_monto_pago DECIMAL(10,2),
    IN p_metodo_pago VARCHAR(20)
)
BEGIN
    DECLARE v_venta_id INT;
    DECLARE v_saldo_pendiente DECIMAL(10,2);
    
    -- Manejo de errores
    DECLARE exit handler FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Obtener la venta asociada y verificar saldo en una vista o consulta
    SELECT ventas_id INTO v_venta_id
    FROM apartados 
    WHERE apartados_id = p_apartado_id AND estado = 'Pendiente';

    IF v_venta_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Apartado no encontrado o ya está completado/cancelado.';
    END IF;

    -- Calcular el saldo pendiente (Total de la venta - pagos previos)
    SELECT (v.total - COALESCE(SUM(p.monto), 0)) INTO v_saldo_pendiente
    FROM ventas v
    LEFT JOIN pagos p ON v.ventas_id = p.ventas_id
    WHERE v.ventas_id = v_venta_id
    GROUP BY v.ventas_id;

    IF p_monto_pago > v_saldo_pendiente THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El monto de pago supera el saldo pendiente.';
    END IF;

    -- Registrar el pago de liquidación
    INSERT INTO pagos (monto, metodo, tipo, cajas_id, ventas_id)
    VALUES (p_monto_pago, p_metodo_pago, 'Liquidacion', p_caja_id, v_venta_id);

    -- Si se liquida completamente, cambiar el estado del apartado
    IF p_monto_pago >= v_saldo_pendiente THEN
        UPDATE apartados
        SET estado = 'Completado'
        WHERE apartados_id = p_apartado_id;
    END IF;

    COMMIT;
END$$

-- 2. Trigger para Auditoría de Movimientos (Mermas y Producción)
DROP TRIGGER IF EXISTS `tg_auditoria_movimientos`$$
CREATE TRIGGER `tg_auditoria_movimientos` AFTER INSERT ON `movimientos`
FOR EACH ROW
BEGIN
    DECLARE v_tipo_desc VARCHAR(20);
    DECLARE v_producto_nombre VARCHAR(100);
    
    -- Obtener la descripción del tipo de movimiento
    SELECT descripcion INTO v_tipo_desc FROM tipo_movimiento WHERE tipo_id = NEW.tipo_id;
    
    -- Obtener nombre del producto
    SELECT nombre INTO v_producto_nombre FROM productos WHERE productos_id = NEW.productos_id;

    -- Solo auditar Producción y Mermas (para no duplicar log de Ventas si ya está en otro lado)
    IF v_tipo_desc IN ('Merma', 'Produccion', 'Ajuste') THEN
        INSERT INTO auditoria (tabla, operacion, usuario_mysql, empleado_id, ip_maquina, detalle)
        VALUES (
            'movimientos', 
            'INSERT', 
            CURRENT_USER(), 
            NEW.usuarios_id, 
            COALESCE(@app_ip_maquina, 'LOCAL'),
            CONCAT('Nuevo movimiento: ', v_tipo_desc, ' | Producto: ', v_producto_nombre, ' | Cantidad: ', NEW.cantidad)
        );
    END IF;
END$$

DELIMITER ;
