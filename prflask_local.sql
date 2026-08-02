-- prflask_local.sql
-- Versión corregida de prflask.sql para levantar unAgenda en local.
-- Cambios respecto al dump original:
--   1. Traza: se quita el prefijo de base de datos hardcodeado (bk9yaw96cgi2zyhqfvda)
--   2. Traza: se agrega la columna `Servicio`, usada en todos los INSERT del código pero ausente en el dump
--   3. Se agregan las tablas `cuaderno` y `flashcards`, usadas en main.py pero nunca incluidas en el dump
--   4. Todo se crea en una única base de datos local (ver README: CREATE DATABASE prflask;)

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- usuario (igual que el original)
DROP TABLE IF EXISTS `usuario`;
CREATE TABLE `usuario` (
  `idUsuario` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `correo` varchar(50) NOT NULL,
  `contrasena` varchar(200) NOT NULL,
  `codigo_verificacion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`idUsuario`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Traza (corregida: sin esquema hardcodeado, con columna Servicio)
DROP TABLE IF EXISTS `Traza`;
CREATE TABLE `Traza` (
  `idTraza` int(11) NOT NULL AUTO_INCREMENT,
  `id_Usuario` int(11) DEFAULT NULL,
  `Nombre` varchar(255) DEFAULT NULL,
  `Descripcion` varchar(255) DEFAULT NULL,
  `Hora` varchar(45) DEFAULT NULL,
  `Servicio` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`idTraza`),
  KEY `id_Usuario_idx` (`id_Usuario`),
  CONSTRAINT `idUsuariotraza` FOREIGN KEY (`id_Usuario`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- recordatorios (igual que el original)
DROP TABLE IF EXISTS `recordatorios`;
CREATE TABLE `recordatorios` (
  `idRecordatorio` int(11) NOT NULL AUTO_INCREMENT,
  `idUsuario` int(11) DEFAULT NULL,
  `nombreRecordatorio` varchar(255) NOT NULL,
  `y` int(11) NOT NULL,
  `mm` int(11) NOT NULL,
  `d` int(11) NOT NULL,
  `h` int(11) NOT NULL,
  `m` int(11) NOT NULL,
  PRIMARY KEY (`idRecordatorio`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `recordatorios_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- grupoNotas (corregida: nombre de tabla en la misma capitalización que usa main.py)
DROP TABLE IF EXISTS `grupoNotas`;
CREATE TABLE `grupoNotas` (
  `idNota` int(11) NOT NULL AUTO_INCREMENT,
  `idUsuario` int(11) DEFAULT NULL,
  `numGrupo` int(11) DEFAULT NULL,
  `porcentaje` float DEFAULT NULL,
  `nota` float DEFAULT NULL,
  PRIMARY KEY (`idNota`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `gruponotas_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- horario (igual que el original)
DROP TABLE IF EXISTS `horario`;
CREATE TABLE `horario` (
  `idHorario` int(11) NOT NULL AUTO_INCREMENT,
  `idUsuario` int(11) NOT NULL,
  `evento` varchar(255) NOT NULL,
  `horaInicio` int(5) NOT NULL,
  `horaFin` int(5) NOT NULL,
  `diaSemana` varchar(15) NOT NULL,
  PRIMARY KEY (`idHorario`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `horario_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- password_reset_tokens (igual que el original)
DROP TABLE IF EXISTS `password_reset_tokens`;
CREATE TABLE `password_reset_tokens` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `token` varchar(255) NOT NULL,
  `created_at` datetime NOT NULL,
  `expiration` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- cuaderno (NUEVA: reconstruida a partir de las queries de main.py)
-- Columnas deducidas de: INSERT INTO cuaderno (id_usuario, nombreCuaderno, contenido, modoOscuro)
-- y de las referencias a id_cuaderno en los SELECT/UPDATE/DELETE
DROP TABLE IF EXISTS `cuaderno`;
CREATE TABLE `cuaderno` (
  `id_cuaderno` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `nombreCuaderno` varchar(255) NOT NULL,
  `contenido` longtext,
  `modoOscuro` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id_cuaderno`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `cuaderno_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- flashcards (NUEVA: reconstruida a partir de las queries de main.py)
-- Columnas deducidas de: INSERT INTO flashcards(id_Usuario, nombreMazo, pista, respuesta, dia, mes, año)
DROP TABLE IF EXISTS `flashcards`;
CREATE TABLE `flashcards` (
  `id_flashcard` int(11) NOT NULL AUTO_INCREMENT,
  `id_Usuario` int(11) NOT NULL,
  `nombreMazo` varchar(255) NOT NULL,
  `pista` varchar(255) NOT NULL,
  `respuesta` varchar(255) NOT NULL,
  `dia` int(11) DEFAULT NULL,
  `mes` int(11) DEFAULT NULL,
  `año` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_flashcard`),
  KEY `id_Usuario` (`id_Usuario`),
  CONSTRAINT `flashcards_ibfk_1` FOREIGN KEY (`id_Usuario`) REFERENCES `usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
