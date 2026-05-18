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
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `file`
--

LOCK TABLES `file` WRITE;
/*!40000 ALTER TABLE `file` DISABLE KEYS */;
INSERT INTO `file` VALUES (18,'万爱华','jpg',21,'http://127.0.0.1:8000/images/906824d1fcdd47cfbe2e67449a834956.jpg',0,1,'4b32eea3978252f6bfb72027931c6a4b'),(19,'太阳花狗狗','jpg',16,'http://127.0.0.1:8000/images/255a70ac563a44da9d8243ed0fa20bb2.jpg',0,1,'c8ff607826186b45f5e16d07376c61ac'),(20,'test','jpg',88,'http://127.0.0.1:8000/images/77a5f258c17d47019e86466ee973bcdb.jpg',0,1,'bd34c492c6349e0c80507614e69f439c');
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
-- Table structure for table `rate`
--

DROP TABLE IF EXISTS `rate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rate` (
  `trackid` int(11) NOT NULL COMMENT '轨迹编号',
  `passrate` float DEFAULT NULL COMMENT '达标率',
  `productionrate` float DEFAULT NULL COMMENT '生产率',
  `timerate` float DEFAULT NULL COMMENT '时间利用率',
  PRIMARY KEY (`trackid`),
  CONSTRAINT `fk_rate_track` FOREIGN KEY (`trackid`) REFERENCES `track` (`trackid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='效率表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rate`
--

LOCK TABLES `rate` WRITE;
/*!40000 ALTER TABLE `rate` DISABLE KEYS */;
/*!40000 ALTER TABLE `rate` ENABLE KEYS */;
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
  `flag` varchar(45) NOT NULL,
  PRIMARY KEY (`id`,`flag`),
  UNIQUE KEY `flag` (`flag`),
  UNIQUE KEY `flag_2` (`flag`)
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
  PRIMARY KEY (`role_id`,`menu_id`),
  KEY `fk_role_menu_menu` (`menu_id`),
  CONSTRAINT `fk_role_menu_menu` FOREIGN KEY (`menu_id`) REFERENCES `menu` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_role_menu_role` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_menu`
--

LOCK TABLES `role_menu` WRITE;
/*!40000 ALTER TABLE `role_menu` DISABLE KEYS */;
INSERT INTO `role_menu` VALUES (1,1),(2,1),(1,3),(2,3),(1,4),(1,5),(2,5),(1,6),(1,7);
/*!40000 ALTER TABLE `role_menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `track`
--

DROP TABLE IF EXISTS `track`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `track` (
  `trackid` int(11) NOT NULL COMMENT '轨迹编号',
  `starttime` datetime DEFAULT NULL COMMENT '开始时间',
  `endtime` datetime DEFAULT NULL COMMENT '结束时间',
  `width` float DEFAULT NULL COMMENT '幅宽',
  `totalpoints` int(11) DEFAULT NULL COMMENT '轨迹点总数',
  PRIMARY KEY (`trackid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='地块轨迹表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `track`
--

LOCK TABLES `track` WRITE;
/*!40000 ALTER TABLE `track` DISABLE KEYS */;
/*!40000 ALTER TABLE `track` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `trackpoints`
--

DROP TABLE IF EXISTS `trackpoints`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `trackpoints` (
  `trackid` int(11) NOT NULL COMMENT '轨迹编号',
  `id` int(11) NOT NULL COMMENT '序列号',
  `gpstime` datetime NOT NULL COMMENT 'GPS时间',
  `lon` decimal(10,6) NOT NULL COMMENT '经度',
  `lat` decimal(10,6) NOT NULL COMMENT '纬度',
  `x` double NOT NULL COMMENT 'x',
  `y` double NOT NULL COMMENT 'y',
  `velocity` float NOT NULL COMMENT '速度',
  `course` float NOT NULL COMMENT '航向',
  `workstatus` tinyint(1) NOT NULL COMMENT '工作状态',
  `width` float NOT NULL COMMENT '幅宽',
  `depth` int(11) NOT NULL COMMENT '深度',
  `depthstandard` int(11) NOT NULL COMMENT '深度标准值',
  PRIMARY KEY (`trackid`,`id`),
  KEY `fk_trackpoints_track` (`trackid`),
  CONSTRAINT `fk_trackpoints_track` FOREIGN KEY (`trackid`) REFERENCES `track` (`trackid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='轨迹点表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `trackpoints`
--

LOCK TABLES `trackpoints` WRITE;
/*!40000 ALTER TABLE `trackpoints` DISABLE KEYS */;
/*!40000 ALTER TABLE `trackpoints` ENABLE KEYS */;
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
  PRIMARY KEY (`id`),
  KEY `fk_user_role_flag` (`role`),
  CONSTRAINT `fk_user_role_flag` FOREIGN KEY (`role`) REFERENCES `role` (`flag`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin','21232f297a57a5a743894a0e4a801fc3','管理员','wanaihua7@gmail.com','17779161007','北京市房山区','2022-11-06 03:20:11','http://127.0.0.1:8000/images/77a5f258c17d47019e86466ee973bcdb.jpg','admin'),(3,'万爱华','32834d6db97dba6b948be75076eab4f0','愚华','3062635305@qq.com','17779161007','江西南昌','2022-11-06 12:19:09','http://localhost:8090/file/cd22f38f71ae4678bbe8c1de69befc12.jpg','user');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `work`
--

DROP TABLE IF EXISTS `work`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `work` (
  `trackid` int(11) NOT NULL COMMENT '轨迹编号',
  `worktime` double DEFAULT NULL COMMENT '作业总时长',
  `worklength` double DEFAULT NULL COMMENT '作业总行程',
  `workarea` double DEFAULT NULL COMMENT '作业总面积',
  `avgvelocity` float DEFAULT NULL COMMENT '平均作业速度',
  PRIMARY KEY (`trackid`),
  CONSTRAINT `fk_work_track` FOREIGN KEY (`trackid`) REFERENCES `track` (`trackid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='作业量表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `work`
--

LOCK TABLES `work` WRITE;
/*!40000 ALTER TABLE `work` DISABLE KEYS */;
/*!40000 ALTER TABLE `work` ENABLE KEYS */;
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

-- Dump completed on 2026-05-18 10:25:26
