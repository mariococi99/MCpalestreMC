-- MySQL dump 10.13  Distrib 8.0.25, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: mcpalestremc
-- ------------------------------------------------------
-- Server version	8.0.25

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
-- Table structure for table `corsi`
--

DROP TABLE IF EXISTS `corsi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `corsi` (
  `idcorso` int NOT NULL AUTO_INCREMENT,
  `titolo` varchar(50) DEFAULT NULL,
  `descrizione` varchar(100) DEFAULT NULL,
  `idlocale` int NOT NULL,
  `cf` varchar(17) NOT NULL,
  `datainizio` date DEFAULT NULL,
  `datafine` date DEFAULT NULL,
  `giorno` varchar(10) DEFAULT NULL,
  `orarioinizio` enum('08:00','10:00','12:00','14:00','16:00','18:00','20:00') DEFAULT NULL,
  `sospeso` enum('SOSPESO','ATTIVO') DEFAULT 'ATTIVO',
  PRIMARY KEY (`idcorso`),
  KEY `idlocale_idx` (`idlocale`),
  KEY `cf_idx` (`cf`),
  CONSTRAINT `cfistruttore` FOREIGN KEY (`cf`) REFERENCES `utenti` (`cf`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `idlocale` FOREIGN KEY (`idlocale`) REFERENCES `locali` (`idlocale`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `corsi`
--

LOCK TABLES `corsi` WRITE;
/*!40000 ALTER TABLE `corsi` DISABLE KEYS */;
INSERT INTO `corsi` VALUES (12,'Trampolino','Jump',1,'SONOUNBOXERFORTE','2021-09-01','2021-11-12','Lunedì','08:00','ATTIVO'),(13,'Calisthenich','gne',1,'SONOUNBOXERFORTE','2021-09-01','2021-11-12','Giovedì','14:00','ATTIVO'),(14,'Corsa','Non fumare se vieni al corso',1,'SONOUNBOXERFORTE','2021-08-01','2021-11-30','Giovedì','14:00','ATTIVO'),(15,'Triathlon','3 discipline diverse',1,'SONOUNBOXERFORTE','2021-06-01','2021-10-31','Sabato','10:00','ATTIVO'),(16,'Calcio','',2,'SONOUNBOXERFORTE','2022-01-20','2022-06-07','Venerdì','18:00','ATTIVO');
/*!40000 ALTER TABLE `corsi` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-12-19 19:39:23
