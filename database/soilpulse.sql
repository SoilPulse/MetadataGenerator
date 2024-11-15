-- Adminer 4.8.1 MySQL 10.4.32-MariaDB dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

DROP DATABASE IF EXISTS `soilpulse`;
CREATE DATABASE `soilpulse` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci */;
USE `soilpulse`;

DROP TABLE IF EXISTS `concepts_dictionary`;
CREATE TABLE `concepts_dictionary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) DEFAULT NULL,
  `string` varchar(255) NOT NULL,
  `term` varchar(255) NOT NULL,
  `vocabulary` varchar(100) NOT NULL,
  `uri` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `concepts_dictionary_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `containers`;
CREATE TABLE `containers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_local` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `parent_id_local` int(11) DEFAULT NULL,
  `project_id` int(11) NOT NULL,
  `relative_path` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `date_last_modified` datetime DEFAULT NULL,
  `encoding` varchar(127) DEFAULT NULL,
  `crawler_type` varchar(127) DEFAULT NULL,
  `data_type` varchar(127) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id_local`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `containers_ibfk_4` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `container_concepts`;
CREATE TABLE `container_concepts` (
  `container_id` int(11) NOT NULL,
  `translation_id` int(11) NOT NULL,
  KEY `container_id` (`container_id`),
  KEY `translation_id` (`translation_id`),
  CONSTRAINT `container_concepts_ibfk_5` FOREIGN KEY (`container_id`) REFERENCES `containers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `container_concepts_ibfk_8` FOREIGN KEY (`translation_id`) REFERENCES `concepts_dictionary` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `container_methods`;
CREATE TABLE `container_methods` (
  `container_id` int(11) NOT NULL,
  `translation_id` int(11) NOT NULL,
  KEY `container_id` (`container_id`),
  KEY `translation_id` (`translation_id`),
  CONSTRAINT `container_methods_ibfk_1` FOREIGN KEY (`container_id`) REFERENCES `containers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `container_methods_ibfk_3` FOREIGN KEY (`translation_id`) REFERENCES `methods_dictionary` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `container_units`;
CREATE TABLE `container_units` (
  `container_id` int(11) NOT NULL,
  `translation_id` int(11) NOT NULL,
  KEY `container_id` (`container_id`),
  KEY `translation_id` (`translation_id`),
  CONSTRAINT `container_units_ibfk_1` FOREIGN KEY (`container_id`) REFERENCES `containers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `container_units_ibfk_2` FOREIGN KEY (`translation_id`) REFERENCES `units_dictionary` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `datasets`;
CREATE TABLE `datasets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dataset_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `datasets_ibfk_3` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `datasets_containers`;
CREATE TABLE `datasets_containers` (
  `dataset_id` int(11) NOT NULL,
  `container_id` int(11) NOT NULL,
  KEY `container_id` (`container_id`),
  KEY `dataset_id` (`dataset_id`),
  CONSTRAINT `datasets_containers_ibfk_2` FOREIGN KEY (`container_id`) REFERENCES `containers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `datasets_containers_ibfk_3` FOREIGN KEY (`dataset_id`) REFERENCES `datasets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `methods_dictionary`;
CREATE TABLE `methods_dictionary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) DEFAULT NULL,
  `string` varchar(255) NOT NULL,
  `term` varchar(255) NOT NULL,
  `vocabulary` varchar(100) NOT NULL,
  `uri` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `methods_dictionary_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `projects`;
CREATE TABLE `projects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `doi` varchar(255) DEFAULT NULL,
  `temp_dir` varchar(255) DEFAULT NULL,
  `keep_files` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='stores information about resources';


DROP TABLE IF EXISTS `units_dictionary`;
CREATE TABLE `units_dictionary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_id` int(11) DEFAULT NULL,
  `string` varchar(255) NOT NULL,
  `term` varchar(255) NOT NULL,
  `vocabulary` varchar(100) NOT NULL,
  `uri` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `units_dictionary_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

INSERT INTO `users` (`id`, `username`, `first_name`, `last_name`) VALUES
(1,	'DemoUser',	'Demo',	'User');

DROP TABLE IF EXISTS `user_projects`;
CREATE TABLE `user_projects` (
  `user_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  KEY `user_id` (`user_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `user_resource_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION,
  CONSTRAINT `user_resource_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


-- 2024-11-14 23:33:19
