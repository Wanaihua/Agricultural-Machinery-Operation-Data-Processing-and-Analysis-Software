-- MySQL dump 10.13  Distrib 5.7.34, for Win64 (x86_64)
--
-- Host: localhost    Database: agricultural_machinery_db
-- ------------------------------------------------------
-- Server version	5.7.34-log

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
-- Table structure for table `dict`
--

DROP TABLE IF EXISTS `dict`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dict` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `value` varchar(45) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dict`
--

LOCK TABLES `dict` WRITE;
/*!40000 ALTER TABLE `dict` DISABLE KEYS */;
INSERT INTO `dict` VALUES (1,'user','el-icon-user','icon'),(2,'house','el-icon-house','icon'),(3,'menu','el-icon-menu','icon'),(4,'file','el-icon-document','icon'),(5,'s-custom','el-icon-s-custom','icon'),(6,'s-grid','el-icon-s-grid','icon');
/*!40000 ALTER TABLE `dict` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `file`
--

DROP TABLE IF EXISTS `file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `file` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT '文件名称',
  `type` varchar(255) DEFAULT '文件类型',
  `size` bigint(20) DEFAULT NULL,
  `url` varchar(255) DEFAULT '文件地址',
  `is_delete` tinyint(1) DEFAULT NULL,
  `enable` tinyint(1) DEFAULT NULL,
  `md5` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `file`
--

LOCK TABLES `file` WRITE;
/*!40000 ALTER TABLE `file` DISABLE KEYS */;
INSERT INTO `file` VALUES (1,'万爱华.jpg','jpg',21,'http://localhost:8090/file/cd22f38f71ae4678bbe8c1de69befc12.jpg',1,1,'4b32eea3978252f6bfb72027931c6a4b'),(10,'微信图片_20221106184209.jpg','jpg',87,'http://localhost:8090/file/9c9ce4e560b64bbc852419e769fd41bf.jpg',1,1,'bd34c492c6349e0c80507614e69f439c'),(11,'mountain.jpg','jpg',253,'http://localhost:8090/file/0b71521f6b5540d99ca5c7340675a162.jpg',1,1,'94ab801538bfbe45269af77b397fdf71'),(12,'微信图片_20241102151729.jpg','jpg',167,'http://localhost:8090/file/a92a707e606c4fa785612d7917013370.jpg',1,1,'3682d431e91df5f9207d770301b2c09d'),(13,'QQ截图20240105141322.png','png',202,'http://localhost:8090/file/5e77d128804e47a2b891fa3ff86eac90.png',1,1,'b614f9801a8766389b5e182a62f99315'),(14,'QQ截图20240104204401.png','png',344,'http://localhost:8090/file/a114bd29da4f4226a70e86bed9a8cd0b.png',1,1,'b1e1729d448c161401bf847f3ab2562c'),(15,'demo','png',0,'http://127.0.0.1:8090/images/3c1ab69f0f23498cb5658ac4627195c3.png',1,1,'e99a18c428cb38d5f260853678922e03'),(16,'test','jpg',88,'http://127.0.0.1:8090/images/e628c2937da440c3b1d470956cd69148.jpg',0,1,'bd34c492c6349e0c80507614e69f439c');
/*!40000 ALTER TABLE `file` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `import_log`
--

DROP TABLE IF EXISTS `import_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `import_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '日志唯一ID，自增',
  `admin_id` int(11) NOT NULL COMMENT '执行导入操作的管理员ID，关联user_info表id',
  `file_name` varchar(100) NOT NULL COMMENT '导入的Excel文件名',
  `import_count` int(11) NOT NULL COMMENT '本次导入的数据条数',
  `import_status` varchar(20) NOT NULL COMMENT '导入状态：success（成功）、fail（失败）',
  `error_info` text COMMENT '导入失败时的错误信息，可选',
  `import_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '导入操作时间',
  PRIMARY KEY (`id`),
  KEY `admin_id` (`admin_id`),
  CONSTRAINT `import_log_ibfk_1` FOREIGN KEY (`admin_id`) REFERENCES `user_info` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Excel数据导入日志表，记录管理员导入操作详情';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `import_log`
--

LOCK TABLES `import_log` WRITE;
/*!40000 ALTER TABLE `import_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `import_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `machinery_track`
--

DROP TABLE IF EXISTS `machinery_track`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `machinery_track` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '轨迹记录唯一ID，自增',
  `plot_no` varchar(50) NOT NULL COMMENT '地块编号，用于轨迹查询、数据删除，唯一标识作业地块',
  `gnss_time` datetime NOT NULL COMMENT 'GNSS定位时间，精确到秒级',
  `longitude` decimal(12,6) NOT NULL COMMENT '经度，保留6位小数',
  `latitude` decimal(11,6) NOT NULL COMMENT '纬度，保留6位小数',
  `speed` decimal(8,2) NOT NULL COMMENT '农机行驶速度，保留2位小数',
  `course` decimal(6,2) DEFAULT '0.00' COMMENT '航向角，保留2位小数，可选字段',
  `work_status` varchar(20) NOT NULL COMMENT '工作状态（如：作业中、空闲、停止）',
  `width` decimal(8,2) DEFAULT '0.00' COMMENT '作业幅宽，保留2位小数',
  `plowing_depth` decimal(8,2) NOT NULL COMMENT '耕整深度，保留2位小数',
  `standard_depth` decimal(8,2) NOT NULL COMMENT '深度标准值，保留2位小数，用于计算达标率',
  `import_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '数据导入时间',
  PRIMARY KEY (`id`),
  KEY `idx_plot_no` (`plot_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='农机作业轨迹数据表，存储所有导入的Excel轨迹数据';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `machinery_track`
--

LOCK TABLES `machinery_track` WRITE;
/*!40000 ALTER TABLE `machinery_track` DISABLE KEYS */;
/*!40000 ALTER TABLE `machinery_track` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `path` varchar(255) DEFAULT NULL,
  `icon` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `pid` int(11) DEFAULT NULL,
  `page_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu`
--

LOCK TABLES `menu` WRITE;
/*!40000 ALTER TABLE `menu` DISABLE KEYS */;
INSERT INTO `menu` VALUES (1,'主页','/home','el-icon-house','1',NULL,'Home'),(3,'系统管理','','el-icon-menu',NULL,NULL,NULL),(4,'用户管理','/user','el-icon-user',NULL,3,'User'),(5,'角色管理','/role','el-icon-s-custom',NULL,3,'Role'),(6,'菜单管理','/menu','el-icon-s-grid',NULL,3,'Menu'),(7,'文件管理','/file','el-icon-document',NULL,3,'File');
/*!40000 ALTER TABLE `menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT '名称',
  `description` varchar(255) DEFAULT '描述',
  `flag` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'管理员','管理员','admin'),(2,'普通用户','普通用户','user');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_menu`
--

DROP TABLE IF EXISTS `role_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role_menu` (
  `role_id` int(11) NOT NULL,
  `menu_id` int(11) NOT NULL,
  PRIMARY KEY (`role_id`,`menu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_menu`
--

LOCK TABLES `role_menu` WRITE;
/*!40000 ALTER TABLE `role_menu` DISABLE KEYS */;
INSERT INTO `role_menu` VALUES (1,1),(1,3),(1,4),(1,5),(1,6),(1,7),(2,1),(2,3),(2,5);
/*!40000 ALTER TABLE `role_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(45) DEFAULT '用户名',
  `password` varchar(45) DEFAULT '密码',
  `nickname` varchar(45) DEFAULT '昵称',
  `email` varchar(45) DEFAULT '邮箱',
  `phone` varchar(45) DEFAULT '电话',
  `address` varchar(255) DEFAULT '地址',
  `creat_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `avatar_url` varchar(255) DEFAULT 'URL',
  `role` varchar(45) DEFAULT '角色',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','21232f297a57a5a743894a0e4a801fc3','管理员','wanaihua7@gmail.com','17779161007','北京市房山区','2022-11-06 03:20:11','http://127.0.0.1:8090/images/e628c2937da440c3b1d470956cd69148.jpg','admin'),(3,'万爱华','32834d6db97dba6b948be75076eab4f0','愚华','3062635305@qq.com','17779161007','江西南昌','2022-11-06 12:19:09','http://localhost:8090/file/cd22f38f71ae4678bbe8c1de69befc12.jpg','user');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'agricultural_machinery_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-21 23:25:15
