CREATE DATABASE  IF NOT EXISTS `panaderia` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `panaderia`;
-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: panaderia
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `apartados`
--

DROP TABLE IF EXISTS `apartados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `apartados` (
  `apartados_id` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_entrega` date NOT NULL,
  `estado` enum('Pendiente','Completado','Cancelado') NOT NULL DEFAULT 'Pendiente',
  `clientes_id` int NOT NULL,
  `ventas_id` int NOT NULL,
  PRIMARY KEY (`apartados_id`),
  KEY `clientes_id` (`clientes_id`),
  KEY `ventas_id` (`ventas_id`),
  KEY `idx_apartados_estado` (`estado`),
  KEY `idx_apartados_entrega` (`fecha_entrega`),
  CONSTRAINT `apartados_ibfk_1` FOREIGN KEY (`clientes_id`) REFERENCES `clientes` (`clientes_id`),
  CONSTRAINT `apartados_ibfk_2` FOREIGN KEY (`ventas_id`) REFERENCES `ventas` (`ventas_id`)
) /*!50100 TABLESPACE `ts_transaccional` */ ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `apartados`
--

LOCK TABLES `apartados` WRITE;
/*!40000 ALTER TABLE `apartados` DISABLE KEYS */;
/*!40000 ALTER TABLE `apartados` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tg_validar_fecha_entrega` BEFORE INSERT ON `apartados` FOR EACH ROW BEGIN
    IF NEW.fecha_entrega <= CURDATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La fecha de entrega debe ser una fecha futura';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM productos p
        JOIN (
            SELECT productos_id, SUM(cantidad) AS cantidad_requerida
            FROM detalle_venta
            WHERE ventas_id = NEW.ventas_id
            GROUP BY productos_id
        ) dv ON dv.productos_id = p.productos_id
        WHERE p.stock < dv.cantidad_requerida
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Stock insuficiente para reservar el apartado';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tg_reservar_stock_apartado` AFTER INSERT ON `apartados` FOR EACH ROW BEGIN
    UPDATE productos p
    JOIN (
        SELECT productos_id, SUM(cantidad) AS cantidad_reservada
        FROM detalle_venta
        WHERE ventas_id = NEW.ventas_id
        GROUP BY productos_id
    ) dv ON dv.productos_id = p.productos_id
    SET p.stock = p.stock - dv.cantidad_reservada;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tg_auditoria_apartados` AFTER UPDATE ON `apartados` FOR EACH ROW BEGIN
    IF NEW.estado != OLD.estado THEN
        IF NEW.estado = 'Cancelado' AND OLD.estado <> 'Cancelado' THEN
            UPDATE productos p
            JOIN (
                SELECT productos_id, SUM(cantidad) AS cantidad_liberada
                FROM detalle_venta
                WHERE ventas_id = NEW.ventas_id
                GROUP BY productos_id
            ) dv ON dv.productos_id = p.productos_id
            SET p.stock = p.stock + dv.cantidad_liberada;
        END IF;

        INSERT INTO auditoria (tabla, operacion, usuario_mysql, empleado_id, ip_maquina, detalle)
        VALUES (
            'apartados',
            'UPDATE',
            CURRENT_USER(),
            COALESCE(
                @app_empleado_id,
                (SELECT usuarios_id FROM ventas WHERE ventas_id = NEW.ventas_id LIMIT 1)
            ),
            @app_ip_maquina,
            CONCAT('Apartado ID ', NEW.apartados_id,
                   ' — estado anterior: ', OLD.estado,
                   ' — estado nuevo: ', NEW.estado)
        );
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `auditoria`
--

DROP TABLE IF EXISTS `auditoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auditoria` (
  `auditoria_id` int NOT NULL AUTO_INCREMENT,
  `tabla` varchar(50) NOT NULL,
  `operacion` enum('INSERT','UPDATE','DELETE') NOT NULL,
  `usuario_mysql` varchar(100) NOT NULL,
  `empleado_id` int DEFAULT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `detalle` text,
  `ip_maquina` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`auditoria_id`),
  KEY `empleado_id` (`empleado_id`),
  CONSTRAINT `auditoria_ibfk_1` FOREIGN KEY (`empleado_id`) REFERENCES `usuarios` (`usuarios_id`)
) /*!50100 TABLESPACE `ts_transaccional` */ ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auditoria`
--

LOCK TABLES `auditoria` WRITE;
/*!40000 ALTER TABLE `auditoria` DISABLE KEYS */;
/*!40000 ALTER TABLE `auditoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cajas`
--

DROP TABLE IF EXISTS `cajas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cajas` (
  `cajas_id` int NOT NULL AUTO_INCREMENT,
  `saldo_inicial` decimal(10,2) NOT NULL DEFAULT '0.00',
  `saldo_final` decimal(10,2) DEFAULT NULL,
  `fecha_apertura` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_cierre` datetime DEFAULT NULL,
  `usuarios_id` int NOT NULL,
  PRIMARY KEY (`cajas_id`),
  KEY `usuarios_id` (`usuarios_id`),
  CONSTRAINT `cajas_ibfk_1` FOREIGN KEY (`usuarios_id`) REFERENCES `usuarios` (`usuarios_id`) ON UPDATE CASCADE,
  CONSTRAINT `cajas_chk_1` CHECK ((`saldo_inicial` >= 0))
) /*!50100 TABLESPACE `ts_transaccional` */ ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cajas`
--

LOCK TABLES `cajas` WRITE;
/*!40000 ALTER TABLE `cajas` DISABLE KEYS */;
/*!40000 ALTER TABLE `cajas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categorias_productos`
--

DROP TABLE IF EXISTS `categorias_productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categorias_productos` (
  `categorias_id` tinyint NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY (`categorias_id`),
  UNIQUE KEY `descripcion` (`descripcion`)
) /*!50100 TABLESPACE `ts_inventario` */ ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categorias_productos`
--

LOCK TABLES `categorias_productos` WRITE;
/*!40000 ALTER TABLE `categorias_productos` DISABLE KEYS */;
INSERT INTO `categorias_productos` VALUES (2,'Pan dulce'),(3,'Pan especial'),(1,'Pan salado');
/*!40000 ALTER TABLE `categorias_productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `clientes_id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `telefono` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`clientes_id`),
  KEY `idx_clientes_nombre` (`nombre`),
  CONSTRAINT `clientes_chk_1` CHECK (((`telefono` is null) or regexp_like(`telefono`,_utf8mb4'^[0-9]{10}$')))
) /*!50100 TABLESPACE `ts_transaccional` */ ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
INSERT INTO `clientes` VALUES (1,'Juan Perez','2299010101'),(2,'Maria Garcia','2299020202'),(3,'Ricardo Moctezuma','2299030303'),(4,'Jimena Hernandez','2299040404'),(5,'Roberto Franco','2299050505'),(6,'Laura Maza','2299060606'),(7,'Sergio Luna','2299070707'),(8,'Carmen Lira','2299080808'),(9,'Alberto Ortiz','2299090909'),(10,'Paola Rojas','2299101010'),(11,'Gabriel Sosa','2299111111'),(12,'Marta Vaca','2299121212'),(13,'Tomas Vera','2299131313'),(14,'Lucia Mora','2299141414'),(15,'Felipe Neri','2299151515'),(16,'Daniela Paz','2299161616'),(17,'Hector Rios','2299171717'),(18,'Victoria Sol','2299181818'),(19,'Oscar Mena','2299191919'),(20,'Diana Cruz','2299202020');
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalle_venta`
--

DROP TABLE IF EXISTS `detalle_venta`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalle_venta` (
  `detalle_id` int NOT NULL AUTO_INCREMENT,
  `cantidad` int NOT NULL,
  `precio_historico` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL,
  `ventas_id` int NOT NULL,
  `productos_id` int NOT NULL,
  PRIMARY KEY (`detalle_id`),
  KEY `idx_detalle_ventas_id` (`ventas_id`),
  KEY `idx_detalle_producto_id` (`productos_id`),
  CONSTRAINT `detalle_venta_ibfk_1` FOREIGN KEY (`ventas_id`) REFERENCES `ventas` (`ventas_id`),
  CONSTRAINT `detalle_venta_ibfk_2` FOREIGN KEY (`productos_id`) REFERENCES `productos` (`productos_id`),
  CONSTRAINT `detalle_venta_chk_1` CHECK ((`cantidad` > 0)),
  CONSTRAINT `detalle_venta_chk_2` CHECK ((`precio_historico` > 0)),
  CONSTRAINT `detalle_venta_chk_3` CHECK ((`subtotal` > 0))
) /*!50100 TABLESPACE `ts_transaccional` */ ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalle_venta`
--

LOCK TABLES `detalle_venta` WRITE;
/*!40000 ALTER TABLE `detalle_venta` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalle_venta` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tg_validar_stock_antes_venta` BEFORE INSERT ON `detalle_venta` FOR EACH ROW BEGIN
    DECLARE v_stock_actual INT;

    SELECT stock INTO v_stock_actual
    FROM productos WHERE productos_id = NEW.productos_id;

    IF NEW.cantidad > v_stock_actual THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Stock insuficiente para realizar la venta';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `movimientos`
--

DROP TABLE IF EXISTS `movimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientos` (
  `movimientos_id` int NOT NULL AUTO_INCREMENT,
  `cantidad` int NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tipo_id` tinyint NOT NULL,
  `productos_id` int NOT NULL,
  `usuarios_id` int NOT NULL,
  PRIMARY KEY (`movimientos_id`),
  KEY `usuarios_id` (`usuarios_id`),
  KEY `idx_movimientos_fecha` (`fecha`),
  KEY `idx_movimientos_tipo` (`tipo_id`),
  KEY `idx_movimientos_prod` (`productos_id`),
  CONSTRAINT `movimientos_ibfk_1` FOREIGN KEY (`tipo_id`) REFERENCES `tipo_movimiento` (`tipo_id`),
  CONSTRAINT `movimientos_ibfk_2` FOREIGN KEY (`productos_id`) REFERENCES `productos` (`productos_id`),
  CONSTRAINT `movimientos_ibfk_3` FOREIGN KEY (`usuarios_id`) REFERENCES `usuarios` (`usuarios_id`),
  CONSTRAINT `movimientos_chk_1` CHECK ((`cantidad` > 0))
) /*!50100 TABLESPACE `ts_inventario` */ ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientos`
--

LOCK TABLES `movimientos` WRITE;
/*!40000 ALTER TABLE `movimientos` DISABLE KEYS */;
/*!40000 ALTER TABLE `movimientos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagos`
--

DROP TABLE IF EXISTS `pagos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagos` (
  `pagos_id` int NOT NULL AUTO_INCREMENT,
  `monto` decimal(10,2) NOT NULL,
  `metodo` enum('Efectivo','Tarjeta','Transferencia') NOT NULL,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tipo` enum('Anticipo','Liquidacion','Directo') NOT NULL,
  `cajas_id` int NOT NULL,
  `ventas_id` int NOT NULL,
  PRIMARY KEY (`pagos_id`),
  KEY `cajas_id` (`cajas_id`),
  KEY `idx_pagos_ventas_id` (`ventas_id`),
  KEY `idx_pagos_metodo` (`metodo`),
  CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`cajas_id`) REFERENCES `cajas` (`cajas_id`),
  CONSTRAINT `pagos_ibfk_2` FOREIGN KEY (`ventas_id`) REFERENCES `ventas` (`ventas_id`),
  CONSTRAINT `pagos_chk_1` CHECK ((`monto` > 0))
) /*!50100 TABLESPACE `ts_transaccional` */ ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos`
--

LOCK TABLES `pagos` WRITE;
/*!40000 ALTER TABLE `pagos` DISABLE KEYS */;
/*!40000 ALTER TABLE `pagos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `productos_id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `precio` decimal(8,2) NOT NULL,
  `stock` int NOT NULL DEFAULT '0',
  `tiempo_vida` int DEFAULT NULL,
  `temporadas_id` tinyint NOT NULL,
  `categorias_id` tinyint NOT NULL,
  PRIMARY KEY (`productos_id`),
  KEY `categorias_id` (`categorias_id`),
  KEY `temporadas_id` (`temporadas_id`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`categorias_id`) REFERENCES `categorias_productos` (`categorias_id`) ON UPDATE CASCADE,
  CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`temporadas_id`) REFERENCES `temporadas` (`temporadas_id`) ON UPDATE CASCADE,
  CONSTRAINT `productos_chk_1` CHECK ((`precio` > 0)),
  CONSTRAINT `productos_chk_2` CHECK ((`stock` >= 0))
) /*!50100 TABLESPACE `ts_inventario` */ ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,'Bolillo',2.50,100,1,1,1),(2,'Telera',3.00,80,1,1,1),(3,'Concha Vainilla',12.00,50,2,1,2),(4,'Concha Chocolate',12.00,50,2,1,2),(5,'Dona Azúcar',10.00,60,1,1,2),(6,'Dona Chocolate',12.00,45,1,1,2),(7,'Oreja',14.00,40,3,1,2),(8,'Cuernito Mantequilla',11.00,70,2,1,2),(9,'Mantecada',9.00,50,3,1,2),(10,'Ojo de Buey',15.00,30,2,1,3),(11,'Beso de Mermelada',14.00,35,2,1,2),(12,'Novia',13.00,25,2,1,2),(13,'Piedra',10.00,20,5,1,2),(14,'Polvorón Nuez',11.00,40,7,1,2),(15,'Pambazo',4.00,60,1,1,1),(16,'Garibaldi',16.00,20,2,1,3),(17,'Rebanada con Mantequilla',8.00,50,2,1,2),(18,'Pan de Muerto Azucarado',18.00,0,3,2,2),(19,'Rosca de Reyes (Chica)',250.00,10,4,4,3),(20,'Rosca de Reyes (Grande)',450.00,5,4,4,3);
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tg_auditoria_precios` AFTER UPDATE ON `productos` FOR EACH ROW BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;

    IF NEW.precio != OLD.precio THEN
        INSERT INTO auditoria (tabla, operacion, usuario_mysql, empleado_id, ip_maquina, detalle)
        VALUES ('productos', 'UPDATE', CURRENT_USER(), @app_empleado_id, @app_ip_maquina,
            CONCAT('Producto: ', OLD.nombre,
                   ' — precio anterior: ', OLD.precio,
                   ' — precio nuevo: ', NEW.precio));
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `rol_id` tinyint NOT NULL AUTO_INCREMENT,
  `tipo` varchar(45) NOT NULL,
  PRIMARY KEY (`rol_id`),
  UNIQUE KEY `tipo` (`tipo`)
) /*!50100 TABLESPACE `ts_inventario` */ ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'Administrador'),(2,'Cajero'),(3,'Panadero');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `temporadas`
--

DROP TABLE IF EXISTS `temporadas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `temporadas` (
  `temporadas_id` tinyint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`temporadas_id`),
  UNIQUE KEY `nombre` (`nombre`)
) /*!50100 TABLESPACE `ts_inventario` */ ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `temporadas`
--

LOCK TABLES `temporadas` WRITE;
/*!40000 ALTER TABLE `temporadas` DISABLE KEYS */;
INSERT INTO `temporadas` VALUES (2,'Día de Muertos'),(3,'Navidad'),(4,'Reyes'),(1,'Todo el año');
/*!40000 ALTER TABLE `temporadas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipo_movimiento`
--

DROP TABLE IF EXISTS `tipo_movimiento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tipo_movimiento` (
  `tipo_id` tinyint NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(20) NOT NULL,
  PRIMARY KEY (`tipo_id`),
  UNIQUE KEY `descripcion` (`descripcion`)
) /*!50100 TABLESPACE `ts_inventario` */ ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipo_movimiento`
--

LOCK TABLES `tipo_movimiento` WRITE;
/*!40000 ALTER TABLE `tipo_movimiento` DISABLE KEYS */;
INSERT INTO `tipo_movimiento` VALUES (4,'Ajuste'),(3,'Merma'),(1,'Produccion'),(2,'Venta');
/*!40000 ALTER TABLE `tipo_movimiento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `usuarios_id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `codigo` varchar(255) NOT NULL,
  `rol_id` tinyint NOT NULL,
  PRIMARY KEY (`usuarios_id`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `rol_id` (`rol_id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`rol_id`) ON UPDATE CASCADE
) /*!50100 TABLESPACE `ts_inventario` */ ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Admin Quetzal','admin123',1),(2,'Laura Cajera','cajera456',2),(3,'Pedro Panadero','pan789',3);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `ventas_id` int NOT NULL AUTO_INCREMENT,
  `fecha` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `total` decimal(10,2) NOT NULL,
  `es_apartado` tinyint NOT NULL DEFAULT '0',
  `cancelada` tinyint NOT NULL DEFAULT '0',
  `usuarios_id` int NOT NULL,
  PRIMARY KEY (`ventas_id`),
  KEY `usuarios_id` (`usuarios_id`),
  KEY `idx_ventas_fecha` (`fecha`),
  KEY `idx_ventas_cancelada` (`cancelada`),
  KEY `idx_ventas_es_apartado` (`es_apartado`),
  CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`usuarios_id`) REFERENCES `usuarios` (`usuarios_id`),
  CONSTRAINT `ventas_chk_1` CHECK ((`total` > 0))
) /*!50100 TABLESPACE `ts_transaccional` */ ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tg_auditoria_ventas` AFTER INSERT ON `ventas` FOR EACH ROW BEGIN
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION BEGIN END;

    INSERT INTO auditoria (tabla, operacion, usuario_mysql, empleado_id, ip_maquina, detalle)
    VALUES ('ventas', 'INSERT', CURRENT_USER(), COALESCE(@app_empleado_id, NEW.usuarios_id), @app_ip_maquina,
        CONCAT('Venta ID ', NEW.ventas_id, ' — total: ', NEW.total,
               ' — apartado: ', NEW.es_apartado, ' — usuario: ', NEW.usuarios_id));
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_ventas_no_modificar` BEFORE UPDATE ON `ventas` FOR EACH ROW BEGIN
    IF NEW.total != OLD.total THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El total de una venta no puede modificarse';
    END IF;
    IF NEW.fecha != OLD.fecha THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La fecha de una venta no puede modificarse';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Temporary view structure for view `vista_auditoria_general`
--

DROP TABLE IF EXISTS `vista_auditoria_general`;
/*!50001 DROP VIEW IF EXISTS `vista_auditoria_general`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_auditoria_general` AS SELECT 
 1 AS `auditoria_id`,
 1 AS `fecha`,
 1 AS `empleado`,
 1 AS `rol`,
 1 AS `modulo_afectado`,
 1 AS `operacion`,
 1 AS `detalle`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_balance_produccion`
--

DROP TABLE IF EXISTS `vista_balance_produccion`;
/*!50001 DROP VIEW IF EXISTS `vista_balance_produccion`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_balance_produccion` AS SELECT 
 1 AS `producto`,
 1 AS `categoria`,
 1 AS `unidades_producidas`,
 1 AS `unidades_vendidas`,
 1 AS `unidades_merma`,
 1 AS `stock_actual`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_corte_caja`
--

DROP TABLE IF EXISTS `vista_corte_caja`;
/*!50001 DROP VIEW IF EXISTS `vista_corte_caja`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_corte_caja` AS SELECT 
 1 AS `cajas_id`,
 1 AS `cajero`,
 1 AS `fecha_apertura`,
 1 AS `fecha_cierre`,
 1 AS `saldo_inicial`,
 1 AS `ventas_efectivo`,
 1 AS `ventas_tarjeta`,
 1 AS `ventas_transferencia`,
 1 AS `total_anticipos`,
 1 AS `total_liquidaciones`,
 1 AS `total_efectivo`,
 1 AS `total_tarjeta`,
 1 AS `saldo_esperado_efectivo`,
 1 AS `total_cobrado`,
 1 AS `saldo_final`,
 1 AS `diferencia`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_entregas_hoy`
--

DROP TABLE IF EXISTS `vista_entregas_hoy`;
/*!50001 DROP VIEW IF EXISTS `vista_entregas_hoy`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_entregas_hoy` AS SELECT 
 1 AS `apartados_id`,
 1 AS `cliente`,
 1 AS `telefono`,
 1 AS `producto`,
 1 AS `cantidad`,
 1 AS `total_apartado`,
 1 AS `total_pagado`,
 1 AS `saldo_pendiente`,
 1 AS `fecha_entrega`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_entregas_semana`
--

DROP TABLE IF EXISTS `vista_entregas_semana`;
/*!50001 DROP VIEW IF EXISTS `vista_entregas_semana`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_entregas_semana` AS SELECT 
 1 AS `apartados_id`,
 1 AS `cliente`,
 1 AS `telefono`,
 1 AS `producto`,
 1 AS `cantidad`,
 1 AS `total_apartado`,
 1 AS `total_pagado`,
 1 AS `saldo_pendiente`,
 1 AS `fecha_entrega`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_inventario_critico`
--

DROP TABLE IF EXISTS `vista_inventario_critico`;
/*!50001 DROP VIEW IF EXISTS `vista_inventario_critico`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_inventario_critico` AS SELECT 
 1 AS `productos_id`,
 1 AS `producto`,
 1 AS `stock`,
 1 AS `categoria`,
 1 AS `temporada`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_productos_disponibles`
--

DROP TABLE IF EXISTS `vista_productos_disponibles`;
/*!50001 DROP VIEW IF EXISTS `vista_productos_disponibles`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_productos_disponibles` AS SELECT 
 1 AS `productos_id`,
 1 AS `nombre`,
 1 AS `precio`,
 1 AS `stock`,
 1 AS `tiempo_vida`,
 1 AS `categoria`,
 1 AS `temporada`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_productos_estrella`
--

DROP TABLE IF EXISTS `vista_productos_estrella`;
/*!50001 DROP VIEW IF EXISTS `vista_productos_estrella`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_productos_estrella` AS SELECT 
 1 AS `producto`,
 1 AS `categoria`,
 1 AS `unidades_vendidas`,
 1 AS `total_recaudado`,
 1 AS `porcentaje_ventas`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_productos_proximos_caducar`
--

DROP TABLE IF EXISTS `vista_productos_proximos_caducar`;
/*!50001 DROP VIEW IF EXISTS `vista_productos_proximos_caducar`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_productos_proximos_caducar` AS SELECT 
 1 AS `producto`,
 1 AS `stock`,
 1 AS `tiempo_vida`,
 1 AS `categoria`,
 1 AS `fecha_produccion`,
 1 AS `fecha_caducidad`,
 1 AS `dias_restantes`,
 1 AS `estado_caducidad`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_rentabilidad_productos`
--

DROP TABLE IF EXISTS `vista_rentabilidad_productos`;
/*!50001 DROP VIEW IF EXISTS `vista_rentabilidad_productos`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_rentabilidad_productos` AS SELECT 
 1 AS `producto`,
 1 AS `categoria`,
 1 AS `ingresos`,
 1 AS `perdida_merma`,
 1 AS `rentabilidad_neta`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_resumen_dia`
--

DROP TABLE IF EXISTS `vista_resumen_dia`;
/*!50001 DROP VIEW IF EXISTS `vista_resumen_dia`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_resumen_dia` AS SELECT 
 1 AS `dia`,
 1 AS `ventas_directas`,
 1 AS `ingresos_ventas`,
 1 AS `apartados_creados`,
 1 AS `anticipos_cobrados`,
 1 AS `liquidaciones_cobradas`,
 1 AS `unidades_producidas`,
 1 AS `unidades_merma`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_saldos_apartados`
--

DROP TABLE IF EXISTS `vista_saldos_apartados`;
/*!50001 DROP VIEW IF EXISTS `vista_saldos_apartados`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_saldos_apartados` AS SELECT 
 1 AS `apartados_id`,
 1 AS `cliente`,
 1 AS `telefono`,
 1 AS `producto`,
 1 AS `cantidad`,
 1 AS `total_apartado`,
 1 AS `total_pagado`,
 1 AS `saldo_pendiente`,
 1 AS `fecha_apartado`,
 1 AS `fecha_entrega`,
 1 AS `estado`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vista_ventas_por_periodo`
--

DROP TABLE IF EXISTS `vista_ventas_por_periodo`;
/*!50001 DROP VIEW IF EXISTS `vista_ventas_por_periodo`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vista_ventas_por_periodo` AS SELECT 
 1 AS `dia`,
 1 AS `num_ventas`,
 1 AS `unidades_vendidas`,
 1 AS `total_recaudado`,
 1 AS `ticket_promedio`,
 1 AS `semana`,
 1 AS `mes`,
 1 AS `anio`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping events for database 'panaderia'
--

--
-- Dumping routines for database 'panaderia'
--
/*!50003 DROP PROCEDURE IF EXISTS `sp_AbrirCaja` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_AbrirCaja`(
    IN p_usuario_id INT,
    IN p_saldo_inicial DECIMAL(10,2)
)
BEGIN
    IF EXISTS (SELECT 1 FROM cajas WHERE fecha_cierre IS NULL) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ya existe un turno de caja abierto';
    ELSE
        INSERT INTO cajas (saldo_inicial, fecha_apertura, usuarios_id)
        VALUES (p_saldo_inicial, NOW(), p_usuario_id);
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_AgregarProducto` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_AgregarProducto`(
    IN p_nombre VARCHAR(100),
    IN p_precio DECIMAL(8,2),
    IN p_stock INT,
    IN p_tiempo_vida INT,
    IN p_temporadas_id TINYINT,
    IN p_categorias_id TINYINT
)
BEGIN
    IF p_precio <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El precio debe ser mayor a cero';
    END IF;

    IF p_stock < 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El stock no puede ser negativo';
    END IF;

    INSERT INTO productos (nombre, precio, stock, tiempo_vida, temporadas_id, categorias_id)
    VALUES (p_nombre, p_precio, p_stock, p_tiempo_vida, p_temporadas_id, p_categorias_id);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_CancelarApartado` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_CancelarApartado`(
    IN p_apartado_id INT
)
BEGIN
    DECLARE v_estado VARCHAR(20);
    DECLARE v_venta_id INT;
    DECLARE v_usuario_id INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET @app_empleado_id = NULL;
        RESIGNAL;
    END;

    START TRANSACTION;
        SELECT estado, ventas_id
        INTO v_estado, v_venta_id
        FROM apartados
        WHERE apartados_id = p_apartado_id
        FOR UPDATE;

        IF v_estado IS NULL THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El apartado indicado no existe';
        END IF;

        IF v_estado = 'Completado' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No se puede cancelar un apartado ya completado';
        END IF;

        IF v_estado = 'Cancelado' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El apartado ya está cancelado';
        END IF;

        SELECT usuarios_id INTO v_usuario_id
        FROM ventas
        WHERE ventas_id = v_venta_id
        LIMIT 1;

        SET @app_empleado_id = v_usuario_id;
        UPDATE apartados SET estado = 'Cancelado' WHERE apartados_id = p_apartado_id;
        SET @app_empleado_id = NULL;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_CancelarVenta` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_CancelarVenta`(
    IN p_venta_id INT,
    IN p_usuario_id INT
)
BEGIN
    DECLARE v_cancelada TINYINT;
    DECLARE v_es_apartado TINYINT;
    DECLARE v_estado_apartado VARCHAR(20);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET @app_empleado_id = NULL;
        RESIGNAL;
    END;

    START TRANSACTION;
        SELECT cancelada, es_apartado
        INTO v_cancelada, v_es_apartado
        FROM ventas
        WHERE ventas_id = p_venta_id
        FOR UPDATE;

        IF v_cancelada IS NULL THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La venta indicada no existe';
        END IF;

        IF v_cancelada = 1 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La venta ya está cancelada';
        END IF;

        SET @app_empleado_id = p_usuario_id;

        IF v_es_apartado = 1 THEN
            SELECT estado INTO v_estado_apartado
            FROM apartados
            WHERE ventas_id = p_venta_id
            LIMIT 1
            FOR UPDATE;

            IF v_estado_apartado IS NULL THEN
                SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La venta es un apartado, pero no tiene un registro asociado en apartados';
            END IF;

            IF v_estado_apartado <> 'Cancelado' THEN
                UPDATE apartados
                SET estado = 'Cancelado'
                WHERE ventas_id = p_venta_id;
            END IF;
        ELSE
            UPDATE productos p
            JOIN (
                SELECT productos_id, SUM(cantidad) AS cantidad_revertida
                FROM detalle_venta
                WHERE ventas_id = p_venta_id
                GROUP BY productos_id
            ) dv ON dv.productos_id = p.productos_id
            SET p.stock = p.stock + dv.cantidad_revertida;

            INSERT INTO movimientos (cantidad, fecha, tipo_id, productos_id, usuarios_id)
            SELECT dv.cantidad_revertida, NOW(), 4, dv.productos_id, p_usuario_id
            FROM (
                SELECT productos_id, SUM(cantidad) AS cantidad_revertida
                FROM detalle_venta
                WHERE ventas_id = p_venta_id
                GROUP BY productos_id
            ) dv;
        END IF;

        UPDATE ventas SET cancelada = 1 WHERE ventas_id = p_venta_id;
        SET @app_empleado_id = NULL;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_CerrarCaja` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_CerrarCaja`(
    IN p_caja_id INT,
    IN p_monto_fisico_contado DECIMAL(10,2)
)
BEGIN
    UPDATE cajas
    SET fecha_cierre = NOW(),
        saldo_final = p_monto_fisico_contado
    WHERE cajas_id = p_caja_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_CrearApartado` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_CrearApartado`(
    IN p_cliente_id INT,
    IN p_usuario_id INT,
    IN p_caja_id INT,
    IN p_total DECIMAL(10,2),
    IN p_anticipo DECIMAL(10,2),
    IN p_producto_id INT,
    IN p_cantidad INT,
    IN p_fecha_entrega DATE,
    IN p_metodo ENUM('Efectivo', 'Tarjeta', 'Transferencia')
)
BEGIN
    CALL sp_CrearApartadoDetallado(
        p_cliente_id,
        p_usuario_id,
        p_caja_id,
        p_total,
        p_anticipo,
        JSON_ARRAY(JSON_OBJECT('productos_id', p_producto_id, 'cantidad', p_cantidad)),
        p_fecha_entrega,
        p_metodo
    );
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_CrearApartadoDetallado` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_CrearApartadoDetallado`(
    IN p_cliente_id INT,
    IN p_usuario_id INT,
    IN p_caja_id INT,
    IN p_total DECIMAL(10,2),
    IN p_anticipo DECIMAL(10,2),
    IN p_detalles JSON,
    IN p_fecha_entrega DATE,
    IN p_metodo ENUM('Efectivo', 'Tarjeta', 'Transferencia')
)
BEGIN
    DECLARE v_venta_id INT;
    DECLARE v_total_calculado DECIMAL(10,2);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET @app_empleado_id = NULL;
        RESIGNAL;
    END;

    IF p_detalles IS NULL OR JSON_TYPE(p_detalles) != 'ARRAY' OR JSON_LENGTH(p_detalles) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El apartado debe incluir al menos un producto';
    END IF;

    START TRANSACTION;
        IF p_fecha_entrega <= CURDATE() THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La fecha de entrega debe ser una fecha futura';
        END IF;

        DROP TEMPORARY TABLE IF EXISTS tmp_detalle_apartado;
        CREATE TEMPORARY TABLE tmp_detalle_apartado (
            productos_id INT NOT NULL,
            cantidad INT NOT NULL
        );

        INSERT INTO tmp_detalle_apartado (productos_id, cantidad)
        SELECT jt.productos_id, jt.cantidad
        FROM JSON_TABLE(
            p_detalles,
            '$[*]' COLUMNS (
                productos_id INT PATH '$.productos_id',
                cantidad INT PATH '$.cantidad'
            )
        ) AS jt;

        IF EXISTS (
            SELECT 1
            FROM tmp_detalle_apartado
            WHERE productos_id IS NULL OR cantidad IS NULL OR cantidad <= 0
        ) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cada detalle debe incluir un producto válido y una cantidad mayor a cero';
        END IF;

        IF EXISTS (
            SELECT 1
            FROM tmp_detalle_apartado td
            LEFT JOIN productos p ON p.productos_id = td.productos_id
            WHERE p.productos_id IS NULL
        ) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Uno o más productos no existen';
        END IF;

        SELECT p.productos_id
        FROM productos p
        JOIN (
            SELECT productos_id, SUM(cantidad) AS cantidad_requerida
            FROM tmp_detalle_apartado
            GROUP BY productos_id
        ) td ON td.productos_id = p.productos_id
        FOR UPDATE;

        IF EXISTS (
            SELECT 1
            FROM productos p
            JOIN (
                SELECT productos_id, SUM(cantidad) AS cantidad_requerida
                FROM tmp_detalle_apartado
                GROUP BY productos_id
            ) td ON td.productos_id = p.productos_id
            WHERE p.stock < td.cantidad_requerida
        ) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente para realizar el apartado';
        END IF;

        SELECT ROUND(SUM(td.cantidad * p.precio), 2) INTO v_total_calculado
        FROM tmp_detalle_apartado td
        JOIN productos p ON p.productos_id = td.productos_id;

        IF ROUND(p_total, 2) <> v_total_calculado THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El total enviado no coincide con el detalle del apartado';
        END IF;

        IF p_anticipo < (v_total_calculado * 0.20) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El anticipo debe ser mayor o igual al 20% del total';
        END IF;

        SET @app_empleado_id = p_usuario_id;

        INSERT INTO ventas (fecha, total, es_apartado, cancelada, usuarios_id)
        VALUES (NOW(), v_total_calculado, 1, 0, p_usuario_id);

        SET v_venta_id = LAST_INSERT_ID();

        INSERT INTO detalle_venta (cantidad, precio_historico, subtotal, ventas_id, productos_id)
        SELECT td.cantidad, p.precio, (td.cantidad * p.precio), v_venta_id, td.productos_id
        FROM tmp_detalle_apartado td
        JOIN productos p ON p.productos_id = td.productos_id;

        INSERT INTO apartados (fecha, fecha_entrega, estado, clientes_id, ventas_id)
        VALUES (NOW(), p_fecha_entrega, 'Pendiente', p_cliente_id, v_venta_id);

        INSERT INTO movimientos (cantidad, fecha, tipo_id, productos_id, usuarios_id)
        SELECT td.cantidad_requerida, NOW(), 2, td.productos_id, p_usuario_id
        FROM (
            SELECT productos_id, SUM(cantidad) AS cantidad_requerida
            FROM tmp_detalle_apartado
            GROUP BY productos_id
        ) td;

        INSERT INTO pagos (monto, metodo, fecha, tipo, cajas_id, ventas_id)
        VALUES (p_anticipo, p_metodo, NOW(), 'Anticipo', p_caja_id, v_venta_id);

        DROP TEMPORARY TABLE IF EXISTS tmp_detalle_apartado;
        SET @app_empleado_id = NULL;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_LiquidarApartado` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_LiquidarApartado`(
    IN p_apartado_id INT,
    IN p_caja_id INT,
    IN p_monto_pago DECIMAL(10,2),
    IN p_metodo ENUM('Efectivo', 'Tarjeta', 'Transferencia')
)
BEGIN
    DECLARE v_venta_id INT;
    DECLARE v_total_venta DECIMAL(10,2);
    DECLARE v_pagado_acumulado DECIMAL(10,2);
    DECLARE v_saldo_pendiente DECIMAL(10,2);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET @app_empleado_id = NULL;
        RESIGNAL;
    END;

    START TRANSACTION;
        SELECT ventas_id INTO v_venta_id
        FROM apartados WHERE apartados_id = p_apartado_id FOR UPDATE;

        SELECT total INTO v_total_venta
        FROM ventas WHERE ventas_id = v_venta_id;

        SELECT IFNULL(SUM(monto), 0) INTO v_pagado_acumulado
        FROM pagos WHERE ventas_id = v_venta_id;

        SET v_saldo_pendiente = v_total_venta - v_pagado_acumulado;

        IF p_monto_pago < v_saldo_pendiente THEN
            SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'El monto no cubre el saldo pendiente. Se requiere la liquidación total';
        END IF;

        SET @app_empleado_id = (
            SELECT usuarios_id
            FROM ventas
            WHERE ventas_id = v_venta_id
            LIMIT 1
        );

        UPDATE apartados SET estado = 'Completado' WHERE apartados_id = p_apartado_id;

        INSERT INTO pagos (monto, metodo, fecha, tipo, cajas_id, ventas_id)
        VALUES (p_monto_pago, p_metodo, NOW(), 'Liquidacion', p_caja_id, v_venta_id);
        SET @app_empleado_id = NULL;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_ModificarPrecioProducto` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_ModificarPrecioProducto`(
    IN p_producto_id INT,
    IN p_precio_nuevo DECIMAL(8,2),
    IN p_usuario_id INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        SET @app_empleado_id = NULL;
        RESIGNAL;
    END;

    IF p_precio_nuevo <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El precio debe ser mayor a cero';
    END IF;

    SET @app_empleado_id = p_usuario_id;
    UPDATE productos SET precio = p_precio_nuevo WHERE productos_id = p_producto_id;
    SET @app_empleado_id = NULL;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_ModificarStockInicial` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_ModificarStockInicial`(
    IN p_usuario_id INT,
    IN p_producto_id INT,
    IN p_cantidad_nueva INT
)
BEGIN
    DECLARE v_stock_anterior INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        SELECT stock INTO v_stock_anterior
        FROM productos WHERE productos_id = p_producto_id FOR UPDATE;

        UPDATE productos SET stock = p_cantidad_nueva WHERE productos_id = p_producto_id;

        INSERT INTO movimientos (cantidad, fecha, tipo_id, productos_id, usuarios_id)
        VALUES (ABS(p_cantidad_nueva - v_stock_anterior), NOW(), 4, p_producto_id, p_usuario_id);
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_ObtenerCajaActiva` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_ObtenerCajaActiva`()
BEGIN
    SELECT cajas_id, saldo_inicial, fecha_apertura, usuarios_id
    FROM cajas
    WHERE fecha_cierre IS NULL
    LIMIT 1;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_RegistrarCliente` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_RegistrarCliente`(
    IN p_nombre VARCHAR(100),
    IN p_telefono VARCHAR(10)
)
BEGIN
    IF p_telefono IS NOT NULL AND p_telefono NOT REGEXP '^[0-9]{10}$' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El teléfono debe tener exactamente 10 dígitos';
    END IF;

    INSERT INTO clientes (nombre, telefono) VALUES (p_nombre, p_telefono);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_RegistrarMerma` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_RegistrarMerma`(
    IN p_usuario_id INT,
    IN p_producto_id INT,
    IN p_cantidad INT
)
BEGIN
    DECLARE v_stock_actual INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        SELECT stock INTO v_stock_actual
        FROM productos WHERE productos_id = p_producto_id FOR UPDATE;

        IF v_stock_actual < p_cantidad THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La merma no puede ser mayor al stock disponible';
        END IF;

        UPDATE productos SET stock = stock - p_cantidad WHERE productos_id = p_producto_id;

        INSERT INTO movimientos (cantidad, fecha, tipo_id, productos_id, usuarios_id)
        VALUES (p_cantidad, NOW(), 3, p_producto_id, p_usuario_id);
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_RegistrarProduccion` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_RegistrarProduccion`(
    IN p_usuario_id INT,
    IN p_producto_id INT,
    IN p_cantidad INT
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
        UPDATE productos SET stock = stock + p_cantidad WHERE productos_id = p_producto_id;

        INSERT INTO movimientos (cantidad, fecha, tipo_id, productos_id, usuarios_id)
        VALUES (p_cantidad, NOW(), 1, p_producto_id, p_usuario_id);
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_RegistrarVentaDirecta` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_RegistrarVentaDirecta`(
    IN p_usuario_id INT,
    IN p_caja_id INT,
    IN p_total DECIMAL(10,2),
    IN p_producto_id INT,
    IN p_cantidad INT,
    IN p_metodo ENUM('Efectivo', 'Tarjeta', 'Transferencia')
)
BEGIN
    CALL sp_RegistrarVentaDirectaDetallada(
        p_usuario_id,
        p_caja_id,
        p_total,
        JSON_ARRAY(JSON_OBJECT('productos_id', p_producto_id, 'cantidad', p_cantidad)),
        p_metodo
    );
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_RegistrarVentaDirectaDetallada` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_RegistrarVentaDirectaDetallada`(
    IN p_usuario_id INT,
    IN p_caja_id INT,
    IN p_total DECIMAL(10,2),
    IN p_detalles JSON,
    IN p_metodo ENUM('Efectivo', 'Tarjeta', 'Transferencia')
)
BEGIN
    DECLARE v_venta_id INT;
    DECLARE v_total_calculado DECIMAL(10,2);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET @app_empleado_id = NULL;
        RESIGNAL;
    END;

    IF p_detalles IS NULL OR JSON_TYPE(p_detalles) != 'ARRAY' OR JSON_LENGTH(p_detalles) = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'La venta debe incluir al menos un producto';
    END IF;

    START TRANSACTION;
        DROP TEMPORARY TABLE IF EXISTS tmp_detalle_venta;
        CREATE TEMPORARY TABLE tmp_detalle_venta (
            productos_id INT NOT NULL,
            cantidad INT NOT NULL
        );

        INSERT INTO tmp_detalle_venta (productos_id, cantidad)
        SELECT jt.productos_id, jt.cantidad
        FROM JSON_TABLE(
            p_detalles,
            '$[*]' COLUMNS (
                productos_id INT PATH '$.productos_id',
                cantidad INT PATH '$.cantidad'
            )
        ) AS jt;

        IF EXISTS (
            SELECT 1
            FROM tmp_detalle_venta
            WHERE productos_id IS NULL OR cantidad IS NULL OR cantidad <= 0
        ) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cada detalle debe incluir un producto válido y una cantidad mayor a cero';
        END IF;

        IF EXISTS (
            SELECT 1
            FROM tmp_detalle_venta td
            LEFT JOIN productos p ON p.productos_id = td.productos_id
            WHERE p.productos_id IS NULL
        ) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Uno o más productos no existen';
        END IF;

        SELECT p.productos_id
        FROM productos p
        JOIN (
            SELECT productos_id, SUM(cantidad) AS cantidad_requerida
            FROM tmp_detalle_venta
            GROUP BY productos_id
        ) td ON td.productos_id = p.productos_id
        FOR UPDATE;

        IF EXISTS (
            SELECT 1
            FROM productos p
            JOIN (
                SELECT productos_id, SUM(cantidad) AS cantidad_requerida
                FROM tmp_detalle_venta
                GROUP BY productos_id
            ) td ON td.productos_id = p.productos_id
            WHERE p.stock < td.cantidad_requerida
        ) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuficiente para realizar la venta';
        END IF;

        SELECT ROUND(SUM(td.cantidad * p.precio), 2) INTO v_total_calculado
        FROM tmp_detalle_venta td
        JOIN productos p ON p.productos_id = td.productos_id;

        IF ROUND(p_total, 2) <> v_total_calculado THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El total enviado no coincide con el detalle de la venta';
        END IF;

        SET @app_empleado_id = p_usuario_id;

        INSERT INTO ventas (fecha, total, es_apartado, cancelada, usuarios_id)
        VALUES (NOW(), v_total_calculado, 0, 0, p_usuario_id);

        SET v_venta_id = LAST_INSERT_ID();

        INSERT INTO detalle_venta (cantidad, precio_historico, subtotal, ventas_id, productos_id)
        SELECT td.cantidad, p.precio, (td.cantidad * p.precio), v_venta_id, td.productos_id
        FROM tmp_detalle_venta td
        JOIN productos p ON p.productos_id = td.productos_id;

        UPDATE productos p
        JOIN (
            SELECT productos_id, SUM(cantidad) AS cantidad_requerida
            FROM tmp_detalle_venta
            GROUP BY productos_id
        ) td ON td.productos_id = p.productos_id
        SET p.stock = p.stock - td.cantidad_requerida;

        INSERT INTO movimientos (cantidad, fecha, tipo_id, productos_id, usuarios_id)
        SELECT td.cantidad_requerida, NOW(), 2, td.productos_id, p_usuario_id
        FROM (
            SELECT productos_id, SUM(cantidad) AS cantidad_requerida
            FROM tmp_detalle_venta
            GROUP BY productos_id
        ) td;

        INSERT INTO pagos (monto, metodo, fecha, tipo, cajas_id, ventas_id)
        VALUES (v_total_calculado, p_metodo, NOW(), 'Directo', p_caja_id, v_venta_id);

        DROP TEMPORARY TABLE IF EXISTS tmp_detalle_venta;
        SET @app_empleado_id = NULL;
    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Final view structure for view `vista_auditoria_general`
--

/*!50001 DROP VIEW IF EXISTS `vista_auditoria_general`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_auditoria_general` AS select `a`.`auditoria_id` AS `auditoria_id`,`a`.`fecha` AS `fecha`,`u`.`nombre` AS `empleado`,`r`.`tipo` AS `rol`,`a`.`tabla` AS `modulo_afectado`,`a`.`operacion` AS `operacion`,`a`.`detalle` AS `detalle` from ((`auditoria` `a` left join `usuarios` `u` on((`a`.`empleado_id` = `u`.`usuarios_id`))) left join `roles` `r` on((`u`.`rol_id` = `r`.`rol_id`))) order by `a`.`fecha` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_balance_produccion`
--

/*!50001 DROP VIEW IF EXISTS `vista_balance_produccion`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_balance_produccion` AS select `p`.`nombre` AS `producto`,`cat`.`descripcion` AS `categoria`,ifnull(sum((case when (`m`.`tipo_id` = 1) then `m`.`cantidad` end)),0) AS `unidades_producidas`,ifnull(sum((case when (`m`.`tipo_id` = 2) then `m`.`cantidad` end)),0) AS `unidades_vendidas`,ifnull(sum((case when (`m`.`tipo_id` = 3) then `m`.`cantidad` end)),0) AS `unidades_merma`,`p`.`stock` AS `stock_actual` from ((`productos` `p` join `categorias_productos` `cat` on((`p`.`categorias_id` = `cat`.`categorias_id`))) left join `movimientos` `m` on((`p`.`productos_id` = `m`.`productos_id`))) group by `p`.`productos_id`,`p`.`nombre`,`cat`.`descripcion`,`p`.`stock` order by `unidades_merma` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_corte_caja`
--

/*!50001 DROP VIEW IF EXISTS `vista_corte_caja`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_corte_caja` AS select `ca`.`cajas_id` AS `cajas_id`,`u`.`nombre` AS `cajero`,`ca`.`fecha_apertura` AS `fecha_apertura`,`ca`.`fecha_cierre` AS `fecha_cierre`,`ca`.`saldo_inicial` AS `saldo_inicial`,ifnull(sum((case when ((`pg`.`tipo` = 'Directo') and (`pg`.`metodo` = 'Efectivo')) then `pg`.`monto` end)),0) AS `ventas_efectivo`,ifnull(sum((case when ((`pg`.`tipo` = 'Directo') and (`pg`.`metodo` = 'Tarjeta')) then `pg`.`monto` end)),0) AS `ventas_tarjeta`,ifnull(sum((case when ((`pg`.`tipo` = 'Directo') and (`pg`.`metodo` = 'Transferencia')) then `pg`.`monto` end)),0) AS `ventas_transferencia`,ifnull(sum((case when (`pg`.`tipo` = 'Anticipo') then `pg`.`monto` end)),0) AS `total_anticipos`,ifnull(sum((case when (`pg`.`tipo` = 'Liquidacion') then `pg`.`monto` end)),0) AS `total_liquidaciones`,ifnull(sum((case when (`pg`.`metodo` = 'Efectivo') then `pg`.`monto` end)),0) AS `total_efectivo`,ifnull(sum((case when (`pg`.`metodo` = 'Tarjeta') then `pg`.`monto` end)),0) AS `total_tarjeta`,(`ca`.`saldo_inicial` + ifnull(sum((case when (`pg`.`metodo` = 'Efectivo') then `pg`.`monto` end)),0)) AS `saldo_esperado_efectivo`,ifnull(sum(`pg`.`monto`),0) AS `total_cobrado`,`ca`.`saldo_final` AS `saldo_final`,(`ca`.`saldo_final` - (`ca`.`saldo_inicial` + ifnull(sum((case when (`pg`.`metodo` = 'Efectivo') then `pg`.`monto` end)),0))) AS `diferencia` from ((`cajas` `ca` join `usuarios` `u` on((`ca`.`usuarios_id` = `u`.`usuarios_id`))) left join `pagos` `pg` on((`ca`.`cajas_id` = `pg`.`cajas_id`))) group by `ca`.`cajas_id`,`u`.`nombre`,`ca`.`fecha_apertura`,`ca`.`fecha_cierre`,`ca`.`saldo_inicial`,`ca`.`saldo_final` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_entregas_hoy`
--

/*!50001 DROP VIEW IF EXISTS `vista_entregas_hoy`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_entregas_hoy` AS select `a`.`apartados_id` AS `apartados_id`,`c`.`nombre` AS `cliente`,`c`.`telefono` AS `telefono`,`p`.`nombre` AS `producto`,`dv`.`cantidad` AS `cantidad`,`v`.`total` AS `total_apartado`,ifnull(sum(`pg`.`monto`),0) AS `total_pagado`,(`v`.`total` - ifnull(sum(`pg`.`monto`),0)) AS `saldo_pendiente`,`a`.`fecha_entrega` AS `fecha_entrega` from (((((`apartados` `a` join `clientes` `c` on((`a`.`clientes_id` = `c`.`clientes_id`))) join `ventas` `v` on((`a`.`ventas_id` = `v`.`ventas_id`))) join `detalle_venta` `dv` on((`v`.`ventas_id` = `dv`.`ventas_id`))) join `productos` `p` on((`dv`.`productos_id` = `p`.`productos_id`))) left join `pagos` `pg` on((`v`.`ventas_id` = `pg`.`ventas_id`))) where ((`a`.`estado` = 'Pendiente') and (`a`.`fecha_entrega` = curdate())) group by `a`.`apartados_id`,`c`.`nombre`,`c`.`telefono`,`p`.`nombre`,`dv`.`cantidad`,`v`.`total`,`a`.`fecha_entrega` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_entregas_semana`
--

/*!50001 DROP VIEW IF EXISTS `vista_entregas_semana`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_entregas_semana` AS select `a`.`apartados_id` AS `apartados_id`,`c`.`nombre` AS `cliente`,`c`.`telefono` AS `telefono`,`p`.`nombre` AS `producto`,`dv`.`cantidad` AS `cantidad`,`v`.`total` AS `total_apartado`,ifnull(sum(`pg`.`monto`),0) AS `total_pagado`,(`v`.`total` - ifnull(sum(`pg`.`monto`),0)) AS `saldo_pendiente`,`a`.`fecha_entrega` AS `fecha_entrega` from (((((`apartados` `a` join `clientes` `c` on((`a`.`clientes_id` = `c`.`clientes_id`))) join `ventas` `v` on((`a`.`ventas_id` = `v`.`ventas_id`))) join `detalle_venta` `dv` on((`v`.`ventas_id` = `dv`.`ventas_id`))) join `productos` `p` on((`dv`.`productos_id` = `p`.`productos_id`))) left join `pagos` `pg` on((`v`.`ventas_id` = `pg`.`ventas_id`))) where ((`a`.`estado` = 'Pendiente') and (`a`.`fecha_entrega` between curdate() and (curdate() + interval 7 day))) group by `a`.`apartados_id`,`c`.`nombre`,`c`.`telefono`,`p`.`nombre`,`dv`.`cantidad`,`v`.`total`,`a`.`fecha_entrega` order by `a`.`fecha_entrega` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_inventario_critico`
--

/*!50001 DROP VIEW IF EXISTS `vista_inventario_critico`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_inventario_critico` AS select `p`.`productos_id` AS `productos_id`,`p`.`nombre` AS `producto`,`p`.`stock` AS `stock`,`cat`.`descripcion` AS `categoria`,`t`.`nombre` AS `temporada` from ((`productos` `p` join `categorias_productos` `cat` on((`p`.`categorias_id` = `cat`.`categorias_id`))) join `temporadas` `t` on((`p`.`temporadas_id` = `t`.`temporadas_id`))) where (`p`.`stock` <= 10) order by `p`.`stock` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_productos_disponibles`
--

/*!50001 DROP VIEW IF EXISTS `vista_productos_disponibles`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_productos_disponibles` AS select `p`.`productos_id` AS `productos_id`,`p`.`nombre` AS `nombre`,`p`.`precio` AS `precio`,`p`.`stock` AS `stock`,`p`.`tiempo_vida` AS `tiempo_vida`,`cat`.`descripcion` AS `categoria`,`t`.`nombre` AS `temporada` from ((`productos` `p` join `categorias_productos` `cat` on((`p`.`categorias_id` = `cat`.`categorias_id`))) join `temporadas` `t` on((`p`.`temporadas_id` = `t`.`temporadas_id`))) where (`p`.`stock` > 0) order by `cat`.`descripcion`,`p`.`nombre` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_productos_estrella`
--

/*!50001 DROP VIEW IF EXISTS `vista_productos_estrella`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_productos_estrella` AS select `p`.`nombre` AS `producto`,`cat`.`descripcion` AS `categoria`,sum(`dv`.`cantidad`) AS `unidades_vendidas`,sum(`dv`.`subtotal`) AS `total_recaudado`,round(((sum(`dv`.`subtotal`) * 100) / (select sum(`detalle_venta`.`subtotal`) from (`detalle_venta` join `ventas` on((`detalle_venta`.`ventas_id` = `ventas`.`ventas_id`))) where (`ventas`.`cancelada` = 0))),2) AS `porcentaje_ventas` from (((`detalle_venta` `dv` join `ventas` `v` on((`dv`.`ventas_id` = `v`.`ventas_id`))) join `productos` `p` on((`dv`.`productos_id` = `p`.`productos_id`))) join `categorias_productos` `cat` on((`p`.`categorias_id` = `cat`.`categorias_id`))) where (`v`.`cancelada` = 0) group by `p`.`productos_id`,`p`.`nombre`,`cat`.`descripcion` order by `unidades_vendidas` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_productos_proximos_caducar`
--

/*!50001 DROP VIEW IF EXISTS `vista_productos_proximos_caducar`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_productos_proximos_caducar` AS select `p`.`nombre` AS `producto`,`p`.`stock` AS `stock`,`p`.`tiempo_vida` AS `tiempo_vida`,`cat`.`descripcion` AS `categoria`,cast(min(`m`.`fecha`) as date) AS `fecha_produccion`,(cast(min(`m`.`fecha`) as date) + interval `p`.`tiempo_vida` day) AS `fecha_caducidad`,(to_days((cast(min(`m`.`fecha`) as date) + interval `p`.`tiempo_vida` day)) - to_days(curdate())) AS `dias_restantes`,(case when ((to_days((cast(min(`m`.`fecha`) as date) + interval `p`.`tiempo_vida` day)) - to_days(curdate())) <= 1) then 'Caduca hoy o mañana' when ((to_days((cast(min(`m`.`fecha`) as date) + interval `p`.`tiempo_vida` day)) - to_days(curdate())) <= 3) then 'Caduca pronto' else 'Con tiempo' end) AS `estado_caducidad` from ((`productos` `p` join `categorias_productos` `cat` on((`p`.`categorias_id` = `cat`.`categorias_id`))) join `movimientos` `m` on(((`p`.`productos_id` = `m`.`productos_id`) and (`m`.`tipo_id` = 1)))) where (`p`.`stock` > 0) group by `p`.`productos_id`,`p`.`nombre`,`p`.`stock`,`p`.`tiempo_vida`,`cat`.`descripcion` having (`fecha_caducidad` >= curdate()) order by `dias_restantes` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_rentabilidad_productos`
--

/*!50001 DROP VIEW IF EXISTS `vista_rentabilidad_productos`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_rentabilidad_productos` AS select `p`.`nombre` AS `producto`,`cat`.`descripcion` AS `categoria`,ifnull(sum(`dv`.`subtotal`),0) AS `ingresos`,ifnull(sum((case when (`m`.`tipo_id` = 3) then (`m`.`cantidad` * `p`.`precio`) end)),0) AS `perdida_merma`,(ifnull(sum(`dv`.`subtotal`),0) - ifnull(sum((case when (`m`.`tipo_id` = 3) then (`m`.`cantidad` * `p`.`precio`) end)),0)) AS `rentabilidad_neta` from ((((`productos` `p` join `categorias_productos` `cat` on((`p`.`categorias_id` = `cat`.`categorias_id`))) left join `detalle_venta` `dv` on((`p`.`productos_id` = `dv`.`productos_id`))) left join `ventas` `v` on(((`dv`.`ventas_id` = `v`.`ventas_id`) and (`v`.`cancelada` = 0)))) left join `movimientos` `m` on(((`p`.`productos_id` = `m`.`productos_id`) and (`m`.`tipo_id` = 3)))) group by `p`.`productos_id`,`p`.`nombre`,`cat`.`descripcion` order by `rentabilidad_neta` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_resumen_dia`
--

/*!50001 DROP VIEW IF EXISTS `vista_resumen_dia`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_resumen_dia` AS select curdate() AS `dia`,count(distinct (case when ((`v`.`es_apartado` = 0) and (`v`.`cancelada` = 0)) then `v`.`ventas_id` end)) AS `ventas_directas`,ifnull(sum((case when ((`v`.`es_apartado` = 0) and (`v`.`cancelada` = 0)) then `v`.`total` end)),0) AS `ingresos_ventas`,count(distinct (case when (`v`.`es_apartado` = 1) then `v`.`ventas_id` end)) AS `apartados_creados`,ifnull(sum((case when ((`pg`.`tipo` = 'Anticipo') and (cast(`pg`.`fecha` as date) = curdate())) then `pg`.`monto` end)),0) AS `anticipos_cobrados`,ifnull(sum((case when ((`pg`.`tipo` = 'Liquidacion') and (cast(`pg`.`fecha` as date) = curdate())) then `pg`.`monto` end)),0) AS `liquidaciones_cobradas`,(select ifnull(sum(`m`.`cantidad`),0) from `movimientos` `m` where ((`m`.`tipo_id` = 1) and (cast(`m`.`fecha` as date) = curdate()))) AS `unidades_producidas`,(select ifnull(sum(`m`.`cantidad`),0) from `movimientos` `m` where ((`m`.`tipo_id` = 3) and (cast(`m`.`fecha` as date) = curdate()))) AS `unidades_merma` from (`ventas` `v` left join `pagos` `pg` on((`v`.`ventas_id` = `pg`.`ventas_id`))) where (cast(`v`.`fecha` as date) = curdate()) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_saldos_apartados`
--

/*!50001 DROP VIEW IF EXISTS `vista_saldos_apartados`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_saldos_apartados` AS select `a`.`apartados_id` AS `apartados_id`,`c`.`nombre` AS `cliente`,`c`.`telefono` AS `telefono`,`p`.`nombre` AS `producto`,`dv`.`cantidad` AS `cantidad`,`v`.`total` AS `total_apartado`,ifnull(sum(`pg`.`monto`),0) AS `total_pagado`,(`v`.`total` - ifnull(sum(`pg`.`monto`),0)) AS `saldo_pendiente`,`a`.`fecha` AS `fecha_apartado`,`a`.`fecha_entrega` AS `fecha_entrega`,`a`.`estado` AS `estado` from (((((`apartados` `a` join `clientes` `c` on((`a`.`clientes_id` = `c`.`clientes_id`))) join `ventas` `v` on((`a`.`ventas_id` = `v`.`ventas_id`))) join `detalle_venta` `dv` on((`v`.`ventas_id` = `dv`.`ventas_id`))) join `productos` `p` on((`dv`.`productos_id` = `p`.`productos_id`))) left join `pagos` `pg` on((`v`.`ventas_id` = `pg`.`ventas_id`))) where (`a`.`estado` <> 'Cancelado') group by `a`.`apartados_id`,`c`.`nombre`,`c`.`telefono`,`p`.`nombre`,`dv`.`cantidad`,`v`.`total`,`a`.`fecha`,`a`.`fecha_entrega`,`a`.`estado` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vista_ventas_por_periodo`
--

/*!50001 DROP VIEW IF EXISTS `vista_ventas_por_periodo`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vista_ventas_por_periodo` AS select cast(`v`.`fecha` as date) AS `dia`,count(distinct `v`.`ventas_id`) AS `num_ventas`,sum(`dv`.`cantidad`) AS `unidades_vendidas`,sum(`dv`.`subtotal`) AS `total_recaudado`,round((sum(`dv`.`subtotal`) / count(distinct `v`.`ventas_id`)),2) AS `ticket_promedio`,week(`v`.`fecha`,0) AS `semana`,month(`v`.`fecha`) AS `mes`,year(`v`.`fecha`) AS `anio` from (`ventas` `v` join `detalle_venta` `dv` on((`v`.`ventas_id` = `dv`.`ventas_id`))) where ((`v`.`es_apartado` = 0) and (`v`.`cancelada` = 0)) group by cast(`v`.`fecha` as date),week(`v`.`fecha`,0),month(`v`.`fecha`),year(`v`.`fecha`) order by `dia` desc */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-10 15:00:06
