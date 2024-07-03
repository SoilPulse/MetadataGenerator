-- Adminer 4.8.1 MySQL 10.4.28-MariaDB dump

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
  `project_id` int(11) NOT NULL,
  `path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id_local`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `containers_ibfk_4` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

INSERT INTO `containers` (`id`, `id_local`, `name`, `type`, `parent_id_local`, `project_id`, `path`) VALUES
(1,	1,	'Resource DOI metadata JSON',	'',	NULL,	1,	NULL),
(2,	2,	'Zenodo metadata JSON',	'',	NULL,	1,	NULL),
(3,	3,	'10-toolboxvignette.Rmd',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\10-toolboxvignette.Rmd'),
(4,	4,	'06-lookout.Rmd',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\06-lookout.Rmd'),
(5,	5,	'index.Rmd',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\index.Rmd'),
(6,	6,	'lenz2022.zip',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip'),
(7,	7,	'lenz2022',	'',	6,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022'),
(8,	8,	'01-intro.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\01-intro.Rmd'),
(9,	9,	'02-state_know.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\02-state_know.Rmd'),
(10,	10,	'03-database.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\03-database.Rmd'),
(11,	11,	'03a-code.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\03a-code.Rmd'),
(12,	12,	'04-results.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\04-results.Rmd'),
(13,	13,	'04a-results_PO.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\04a-results_PO.Rmd'),
(14,	14,	'04b-results-statis.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\04b-results-statis.Rmd'),
(15,	15,	'05-discussion.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\05-discussion.Rmd'),
(16,	16,	'05a-reallookout.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\05a-reallookout.Rmd'),
(17,	17,	'06-lookout.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\06-lookout.Rmd'),
(18,	18,	'07-references.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\07-references.Rmd'),
(19,	19,	'08-E3DIssues.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\08-E3DIssues.Rmd'),
(20,	20,	'09-database.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\09-database.Rmd'),
(21,	21,	'10-toolboxvignette.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\10-toolboxvignette.Rmd'),
(22,	22,	'11-varrain.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\11-varrain.Rmd'),
(23,	23,	'comp_infils',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils'),
(24,	24,	'comp_E3D_landlab.Rmd',	'',	23,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\comp_E3D_landlab.Rmd'),
(25,	25,	'comp_infil.R',	'',	23,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\comp_infil.R'),
(26,	26,	'implicite_GA.R',	'',	23,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\implicite_GA.R'),
(27,	27,	'py',	'',	23,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\py'),
(28,	28,	'GA_comparison.ipynb',	'',	27,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\py\\GA_comparison.ipynb'),
(29,	29,	'GA_results.csv',	'',	27,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\py\\GA_results.csv'),
(30,	30,	'database',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database'),
(31,	31,	'csv',	'',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv'),
(32,	32,	'1.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\1.csv'),
(33,	33,	'10.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\10.csv'),
(34,	34,	'100.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\100.csv'),
(35,	35,	'101.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\101.csv'),
(36,	36,	'102.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\102.csv'),
(37,	37,	'104.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\104.csv'),
(38,	38,	'105.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\105.csv'),
(39,	39,	'106.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\106.csv'),
(40,	40,	'107.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\107.csv'),
(41,	41,	'108.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\108.csv'),
(42,	42,	'109.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\109.csv'),
(43,	43,	'11.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\11.csv'),
(44,	44,	'110.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\110.csv'),
(45,	45,	'111.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\111.csv'),
(46,	46,	'112.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\112.csv'),
(47,	47,	'114.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\114.csv'),
(48,	48,	'115.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\115.csv'),
(49,	49,	'116.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\116.csv'),
(50,	50,	'12.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\12.csv'),
(51,	51,	'13.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\13.csv'),
(52,	52,	'14.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\14.csv'),
(53,	53,	'15.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\15.csv'),
(54,	54,	'16.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\16.csv'),
(55,	55,	'17.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\17.csv'),
(56,	56,	'18.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\18.csv'),
(57,	57,	'19.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\19.csv'),
(58,	58,	'2.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\2.csv'),
(59,	59,	'20.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\20.csv'),
(60,	60,	'21.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\21.csv'),
(61,	61,	'22.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\22.csv'),
(62,	62,	'23.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\23.csv'),
(63,	63,	'24.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\24.csv'),
(64,	64,	'25.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\25.csv'),
(65,	65,	'26.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\26.csv'),
(66,	66,	'27.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\27.csv'),
(67,	67,	'28.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\28.csv'),
(68,	68,	'29.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\29.csv'),
(69,	69,	'30.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\30.csv'),
(70,	70,	'31.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\31.csv'),
(71,	71,	'32.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\32.csv'),
(72,	72,	'33.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\33.csv'),
(73,	73,	'34.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\34.csv'),
(74,	74,	'35.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\35.csv'),
(75,	75,	'36.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\36.csv'),
(76,	76,	'37.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\37.csv'),
(77,	77,	'38.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\38.csv'),
(78,	78,	'39.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\39.csv'),
(79,	79,	'4.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\4.csv'),
(80,	80,	'40.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\40.csv'),
(81,	81,	'41.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\41.csv'),
(82,	82,	'42.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\42.csv'),
(83,	83,	'43.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\43.csv'),
(84,	84,	'44.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\44.csv'),
(85,	85,	'45.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\45.csv'),
(86,	86,	'46.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\46.csv'),
(87,	87,	'47.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\47.csv'),
(88,	88,	'48.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\48.csv'),
(89,	89,	'49.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\49.csv'),
(90,	90,	'5.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\5.csv'),
(91,	91,	'50.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\50.csv'),
(92,	92,	'51.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\51.csv'),
(93,	93,	'53.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\53.csv'),
(94,	94,	'54.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\54.csv'),
(95,	95,	'55.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\55.csv'),
(96,	96,	'56.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\56.csv'),
(97,	97,	'58.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\58.csv'),
(98,	98,	'59.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\59.csv'),
(99,	99,	'6.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\6.csv'),
(100,	100,	'60.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\60.csv'),
(101,	101,	'61.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\61.csv'),
(102,	102,	'62.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\62.csv'),
(103,	103,	'64.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\64.csv'),
(104,	104,	'65.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\65.csv'),
(105,	105,	'66.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\66.csv'),
(106,	106,	'67.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\67.csv'),
(107,	107,	'68.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\68.csv'),
(108,	108,	'69.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\69.csv'),
(109,	109,	'7.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\7.csv'),
(110,	110,	'70.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\70.csv'),
(111,	111,	'71.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\71.csv'),
(112,	112,	'72.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\72.csv'),
(113,	113,	'73.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\73.csv'),
(114,	114,	'74.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\74.csv'),
(115,	115,	'75.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\75.csv'),
(116,	116,	'76.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\76.csv'),
(117,	117,	'77.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\77.csv'),
(118,	118,	'78.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\78.csv'),
(119,	119,	'79.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\79.csv'),
(120,	120,	'8.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\8.csv'),
(121,	121,	'80.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\80.csv'),
(122,	122,	'81.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\81.csv'),
(123,	123,	'82.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\82.csv'),
(124,	124,	'83.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\83.csv'),
(125,	125,	'84.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\84.csv'),
(126,	126,	'85.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\85.csv'),
(127,	127,	'86.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\86.csv'),
(128,	128,	'87.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\87.csv'),
(129,	129,	'88.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\88.csv'),
(130,	130,	'89.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\89.csv'),
(131,	131,	'9.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\9.csv'),
(132,	132,	'90.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\90.csv'),
(133,	133,	'92.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\92.csv'),
(134,	134,	'93.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\93.csv'),
(135,	135,	'94.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\94.csv'),
(136,	136,	'95.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\95.csv'),
(137,	137,	'96.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\96.csv'),
(138,	138,	'97.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\97.csv'),
(139,	139,	'98.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\98.csv'),
(140,	140,	'99.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\99.csv'),
(141,	141,	'korrek.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\korrek.csv'),
(142,	142,	'log.txt',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\log.txt'),
(143,	143,	'M1.2.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M1.2.csv'),
(144,	144,	'M1.3.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M1.3.csv'),
(145,	145,	'M2.1.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M2.1.csv'),
(146,	146,	'M2.2.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M2.2.csv'),
(147,	147,	'M3.1.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M3.1.csv'),
(148,	148,	'M3.2.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M3.2.csv'),
(149,	149,	'M4.1.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M4.1.csv'),
(150,	150,	'M5.1.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M5.1.csv'),
(151,	151,	'M5.2.csv',	'',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M5.2.csv'),
(152,	152,	'functions_for_DC.R',	'',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\functions_for_DC.R'),
(153,	153,	'functions_for_visualization.R',	'',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\functions_for_visualization.R'),
(154,	154,	'hydraulic_func.R',	'',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\hydraulic_func.R'),
(155,	155,	'Input',	'',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\Input'),
(156,	156,	'Diss_michael_anlage.csv',	'',	155,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\Input\\Diss_michael_anlage.csv'),
(157,	157,	'michael_rough_annex2.csv',	'',	155,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\Input\\michael_rough_annex2.csv'),
(158,	158,	'readme_Diss_michael_anlage.txt',	'',	155,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\Input\\readme_Diss_michael_anlage.txt'),
(159,	159,	'remarks_on_AnneRuns.txt',	'',	155,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\Input\\remarks_on_AnneRuns.txt'),
(160,	160,	'process',	'',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\process'),
(161,	161,	'ready2.csv',	'',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\ready2.csv'),
(162,	162,	'readytime.csv',	'',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\readytime.csv'),
(163,	163,	'single_file.R',	'',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\single_file.R'),
(164,	164,	'database2',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2'),
(165,	165,	'CALCall.txt',	'',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\CALCall.txt'),
(166,	166,	'Datensatz2.Rmd',	'',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\Datensatz2.Rmd'),
(167,	167,	'derivedparams.csv',	'',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\derivedparams.csv'),
(168,	168,	'HOR.txt',	'',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\HOR.txt'),
(169,	169,	'Macropore.txt',	'',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\Macropore.txt'),
(170,	170,	'prep.R',	'',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\prep.R'),
(171,	171,	'RUNPROPall.txt',	'',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\RUNPROPall.txt'),
(172,	172,	'RUNTEMP.txt',	'',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\RUNTEMP.txt'),
(173,	173,	'SOILall.txt',	'',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\SOILall.txt'),
(174,	174,	'export',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\export'),
(175,	175,	'meta.csv',	'',	174,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\export\\meta.csv'),
(176,	176,	'time.csv',	'',	174,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\export\\time.csv'),
(177,	177,	'index.Rmd',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\index.Rmd'),
(178,	178,	'para_opti',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti'),
(179,	179,	'by_R',	'',	178,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti\\by_R'),
(180,	180,	'aMC_in_R.R',	'',	179,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\aMC_in_R.R'),
(181,	181,	'aMC_in_R_ewid.R',	'',	179,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\aMC_in_R_ewid.R'),
(182,	182,	'avisualization.R',	'',	179,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\avisualization.R'),
(183,	183,	'avisualization2.R',	'',	179,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\avisualization2.R'),
(184,	184,	'preamble.tex',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\preamble.tex'),
(185,	185,	'_output.yml',	'',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\_output.yml'),
(186,	186,	'09-database.Rmd',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\09-database.Rmd'),
(187,	187,	'11-varrain.Rmd',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\11-varrain.Rmd'),
(188,	188,	'08-E3DIssues.Rmd',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\08-E3DIssues.Rmd'),
(189,	189,	'_output.yml',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\_output.yml'),
(190,	190,	'07-references.Rmd',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\07-references.Rmd'),
(191,	191,	'preamble.tex',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\preamble.tex'),
(192,	192,	'03a-code.Rmd',	'',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\03a-code.Rmd');

DROP TABLE IF EXISTS `datasets`;
CREATE TABLE `datasets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_local` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `project_id` int(11) NOT NULL,
  `container_ids` varchar(1023) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `datasets_ibfk_3` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

INSERT INTO `datasets` (`id`, `id_local`, `name`, `project_id`, `container_ids`) VALUES
(1,	0,	'Dataset test 1',	1,	'1|2|6');

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
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='stores information about resources';

INSERT INTO `projects` (`id`, `name`, `doi`, `temp_dir`) VALUES
(1,	'Jonas Lenz\'s dissertation package',	'10.5281/zenodo.6654150',	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1');

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

INSERT INTO `users` (`id`, `username`, `first_name`, `last_name`) VALUES
(1,	'devatjan',	'Jan',	'Devátý');

DROP TABLE IF EXISTS `user_projects`;
CREATE TABLE `user_projects` (
  `user_id` int(11) NOT NULL,
  `project_id` int(11) NOT NULL,
  KEY `user_id` (`user_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `user_resource_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION,
  CONSTRAINT `user_resource_ibfk_2` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

INSERT INTO `user_projects` (`user_id`, `project_id`) VALUES
(1,	1);

-- 2024-07-03 06:32:12
