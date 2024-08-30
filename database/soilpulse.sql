-- Adminer 4.8.1 MySQL 10.4.32-MariaDB dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

USE `soilpulse`;

DROP TABLE IF EXISTS `containers`;
CREATE TABLE `containers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_local` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `parent_id_local` int(11) DEFAULT NULL,
  `crawler_type` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `relative_path` varchar(255) DEFAULT NULL,
  `date_created` datetime DEFAULT NULL,
  `date_last_modified` datetime DEFAULT NULL,
  `encoding` varchar(127) DEFAULT NULL,
  `content` varchar(62047) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id_local`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `containers_ibfk_4` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `datasets`;
CREATE TABLE `datasets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `container_ids` varchar(1023) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `datasets_ibfk_3` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `entities`;
CREATE TABLE `entities` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type_id` int(11) NOT NULL,
  `mapping_id` int(11) NOT NULL,
  `value` varchar(500) DEFAULT NULL,
  `pointer` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `mapping_id` (`mapping_id`),
  CONSTRAINT `entities_ibfk_1` FOREIGN KEY (`mapping_id`) REFERENCES `mappings` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='stores instances of metadata entities belonging to a certain mapping';


DROP TABLE IF EXISTS `mappings`;
CREATE TABLE `mappings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `project_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `mappings_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='stores relations between metadata entity mappings and resources';


DROP TABLE IF EXISTS `projects`;
CREATE TABLE `projects` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `doi` varchar(255) DEFAULT NULL,
  `temp_dir` varchar(255) DEFAULT NULL,
  `keep_files` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='stores information about resources';


DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

TRUNCATE `users`;
INSERT INTO `users` (`id`, `username`, `first_name`, `last_name`) VALUES
(1, 'DemoUser', 'Demo', 'User');


DROP TABLE IF EXISTS `user_projects`;
CREATE TABLE `user_projects` (
  `user_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  KEY `user_id` (`user_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `user_resource_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION,
  CONSTRAINT `user_resource_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `_concepts`;
CREATE TABLE `_concepts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `container_id` int(11) NOT NULL,
  `vocabulary` varchar(50) NOT NULL,
  `uri` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `container_id` (`container_id`),
  CONSTRAINT `_concepts_ibfk_1` FOREIGN KEY (`container_id`) REFERENCES `containers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `_methods`;
CREATE TABLE `_methods` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `container_id` int(11) NOT NULL,
  `vocabulary` varchar(50) NOT NULL,
  `uri` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `container_id` (`container_id`),
  CONSTRAINT `_methods_ibfk_1` FOREIGN KEY (`container_id`) REFERENCES `containers` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


DROP TABLE IF EXISTS `_units`;
CREATE TABLE `_units` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `container_id` int(11) NOT NULL,
  `vocabulary` varchar(50) NOT NULL,
  `uri` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `container_id` (`container_id`),
  CONSTRAINT `_units_ibfk_1` FOREIGN KEY (`container_id`) REFERENCES `containers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


-- 2024-08-20 09:06:58
