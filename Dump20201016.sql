-- MySQL dump 10.13  Distrib 5.7.31, for Linux (x86_64)
--
-- Host: localhost    Database: url_short_db
-- ------------------------------------------------------
-- Server version	5.7.31-0ubuntu0.18.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `url_details`
--

DROP TABLE IF EXISTS `url_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `url_details` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `original_url` varchar(255) DEFAULT NULL,
  `short_url` varchar(255) DEFAULT NULL,
  `visits` varchar(255) DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `url_details`
--

LOCK TABLES `url_details` WRITE;
/*!40000 ALTER TABLE `url_details` DISABLE KEYS */;
INSERT INTO `url_details` VALUES (7,'https://practice.geeksforgeeks.org/courses/online','f48','6','2020-10-15 06:16:53'),(8,'https://en.wikipedia.org/wiki/Geek','muP','2','2020-10-15 06:47:16'),(9,'https://practice.geeksforgeeks.org/courses/','pUO','3','2020-10-15 09:22:36'),(10,'https://www.google.com/','WR7','4','2020-10-16 11:26:18');
/*!40000 ALTER TABLE `url_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `visits`
--

DROP TABLE IF EXISTS `visits`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `visits` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `original_url` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `visits`
--

LOCK TABLES `visits` WRITE;
/*!40000 ALTER TABLE `visits` DISABLE KEYS */;
INSERT INTO `visits` VALUES (8,'https://practice.geeksforgeeks.org/courses/online','2020-10-15 06:16:53'),(9,'https://practice.geeksforgeeks.org/courses/online','2020-10-15 06:17:02'),(10,'https://practice.geeksforgeeks.org/courses/online','2020-10-15 06:17:04'),(11,'https://practice.geeksforgeeks.org/courses/online','2020-10-15 06:17:05'),(12,'https://practice.geeksforgeeks.org/courses/online','2020-10-15 06:17:06'),(13,'https://en.wikipedia.org/wiki/Geek','2020-10-15 06:47:16'),(14,'https://en.wikipedia.org/wiki/Geek','2020-10-15 06:47:35'),(15,'https://practice.geeksforgeeks.org/courses/online','2020-10-15 06:49:28'),(16,'https://practice.geeksforgeeks.org/courses/','2020-10-15 09:22:36'),(17,'https://practice.geeksforgeeks.org/courses/','2020-10-15 09:22:40'),(18,'https://practice.geeksforgeeks.org/courses/','2020-10-15 09:22:41'),(19,'https://www.google.com/','2020-10-16 11:26:18'),(20,'https://www.google.com/','2020-10-16 11:26:33'),(21,'https://www.google.com/','2020-10-16 11:26:37'),(22,'https://www.google.com/','2020-10-16 13:10:57');
/*!40000 ALTER TABLE `visits` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-10-16 18:55:14
