-- Adminer 4.8.1 MySQL 10.4.28-MariaDB dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

DROP DATABASE IF EXISTS `soilpulse`;
CREATE DATABASE `soilpulse` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci */;
USE `soilpulse`;

CREATE TABLE `containers` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_local` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `parent_id_local` int(11) DEFAULT NULL,
  `resource_id` int(11) NOT NULL,
  `path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id_local`),
  KEY `resource_id` (`resource_id`),
  CONSTRAINT `containers_ibfk_4` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

INSERT INTO `containers` (`id`, `id_local`, `name`, `parent_id_local`, `resource_id`, `path`) VALUES
(98,	1,	'Resource DOI metadata JSON',	NULL,	171,	NULL),
(99,	2,	'Zenodo metadata JSON',	NULL,	171,	NULL),
(100,	3,	'neuromorphic_classifier-v0.7.zip',	NULL,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip'),
(101,	4,	'Huitzilo-neuromorphic_classifier-92ce433',	3,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433'),
(102,	5,	'.gitignore',	4,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\.gitignore'),
(103,	6,	'doc',	4,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\doc'),
(104,	7,	'Schmuker, Pfeil, Nawrot - 2014 - A neuromorphic network for generic multivariate data classification.pdf',	6,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\doc\\Schmuker, Pfeil, Nawrot - 2014 - A neuromorphic network for generic multivariate data classification.pdf'),
(105,	8,	'LICENSE',	4,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\LICENSE'),
(106,	9,	'README.md',	4,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\README.md'),
(107,	10,	'src',	4,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src'),
(108,	11,	'.spyderproject',	10,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\.spyderproject'),
(109,	12,	'mnist_classifier_on_spikey.py',	10,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\mnist_classifier_on_spikey.py'),
(110,	13,	'neuclar',	10,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar'),
(111,	14,	'data',	13,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\data'),
(112,	15,	'iris_vrec_pos.npy',	14,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\data\\iris_vrec_pos.npy'),
(113,	16,	'mnist.py',	14,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\data\\mnist.py'),
(114,	17,	'mnist_vrec_pos.npy',	14,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\data\\mnist_vrec_pos.npy'),
(115,	18,	't10k-images-idx3-ubyte.gz',	14,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\data\\t10k-images-idx3-ubyte_gz\\t10k-images-idx3-ubyte'),
(116,	19,	't10k-labels-idx1-ubyte.gz',	14,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\data\\t10k-labels-idx1-ubyte_gz\\t10k-labels-idx1-ubyte'),
(117,	20,	'train-images-idx3-ubyte.gz',	14,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\data\\train-images-idx3-ubyte_gz\\train-images-idx3-ubyte'),
(118,	21,	'train-labels-idx1-ubyte.gz',	14,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\data\\train-labels-idx1-ubyte_gz\\train-labels-idx1-ubyte'),
(119,	22,	'__init__.py',	14,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\data\\__init__.py'),
(120,	23,	'network.py',	13,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\network.py'),
(121,	24,	'network_config.py',	13,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\network_config.py'),
(122,	25,	'network_controller.py',	13,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\network_controller.py'),
(123,	26,	'network_utilities.py',	13,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\network_utilities.py'),
(124,	27,	'vrconvert.py',	13,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\vrconvert.py'),
(125,	28,	'__init__.py',	13,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\neuclar\\__init__.py'),
(126,	29,	'timings.py',	10,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\timings.py'),
(127,	30,	'vrpos-571_3000.npy',	10,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\vrpos-571_3000.npy'),
(128,	31,	'vrpos-57_200.npy',	10,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\vrpos-57_200.npy'),
(129,	32,	'vrpos-57_2000.npy',	10,	171,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\171\\neuromorphic_classifier-v0_7_zip\\Huitzilo-neuromorphic_classifier-92ce433\\src\\vrpos-57_2000.npy'),
(130,	1,	'Resource DOI metadata JSON',	NULL,	172,	NULL),
(131,	2,	'Zenodo metadata JSON',	NULL,	172,	NULL),
(132,	3,	'10-toolboxvignette.Rmd',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\10-toolboxvignette.Rmd'),
(133,	4,	'06-lookout.Rmd',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\06-lookout.Rmd'),
(134,	5,	'index.Rmd',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\index.Rmd'),
(135,	6,	'lenz2022.zip',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip'),
(136,	7,	'lenz2022',	6,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022'),
(137,	8,	'01-intro.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\01-intro.Rmd'),
(138,	9,	'02-state_know.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\02-state_know.Rmd'),
(139,	10,	'03-database.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\03-database.Rmd'),
(140,	11,	'03a-code.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\03a-code.Rmd'),
(141,	12,	'04-results.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\04-results.Rmd'),
(142,	13,	'04a-results_PO.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\04a-results_PO.Rmd'),
(143,	14,	'04b-results-statis.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\04b-results-statis.Rmd'),
(144,	15,	'05-discussion.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\05-discussion.Rmd'),
(145,	16,	'05a-reallookout.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\05a-reallookout.Rmd'),
(146,	17,	'06-lookout.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\06-lookout.Rmd'),
(147,	18,	'07-references.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\07-references.Rmd'),
(148,	19,	'08-E3DIssues.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\08-E3DIssues.Rmd'),
(149,	20,	'09-database.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\09-database.Rmd'),
(150,	21,	'10-toolboxvignette.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\10-toolboxvignette.Rmd'),
(151,	22,	'11-varrain.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\11-varrain.Rmd'),
(152,	23,	'comp_infils',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\comp_infils'),
(153,	24,	'comp_E3D_landlab.Rmd',	23,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\comp_infils\\comp_E3D_landlab.Rmd'),
(154,	25,	'comp_infil.R',	23,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\comp_infils\\comp_infil.R'),
(155,	26,	'implicite_GA.R',	23,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\comp_infils\\implicite_GA.R'),
(156,	27,	'py',	23,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\comp_infils\\py'),
(157,	28,	'GA_comparison.ipynb',	27,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\comp_infils\\py\\GA_comparison.ipynb'),
(158,	29,	'GA_results.csv',	27,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\comp_infils\\py\\GA_results.csv'),
(159,	30,	'database',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database'),
(160,	31,	'csv',	30,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv'),
(161,	32,	'1.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\1.csv'),
(162,	33,	'10.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\10.csv'),
(163,	34,	'100.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\100.csv'),
(164,	35,	'101.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\101.csv'),
(165,	36,	'102.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\102.csv'),
(166,	37,	'104.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\104.csv'),
(167,	38,	'105.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\105.csv'),
(168,	39,	'106.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\106.csv'),
(169,	40,	'107.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\107.csv'),
(170,	41,	'108.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\108.csv'),
(171,	42,	'109.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\109.csv'),
(172,	43,	'11.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\11.csv'),
(173,	44,	'110.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\110.csv'),
(174,	45,	'111.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\111.csv'),
(175,	46,	'112.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\112.csv'),
(176,	47,	'114.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\114.csv'),
(177,	48,	'115.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\115.csv'),
(178,	49,	'116.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\116.csv'),
(179,	50,	'12.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\12.csv'),
(180,	51,	'13.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\13.csv'),
(181,	52,	'14.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\14.csv'),
(182,	53,	'15.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\15.csv'),
(183,	54,	'16.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\16.csv'),
(184,	55,	'17.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\17.csv'),
(185,	56,	'18.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\18.csv'),
(186,	57,	'19.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\19.csv'),
(187,	58,	'2.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\2.csv'),
(188,	59,	'20.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\20.csv'),
(189,	60,	'21.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\21.csv'),
(190,	61,	'22.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\22.csv'),
(191,	62,	'23.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\23.csv'),
(192,	63,	'24.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\24.csv'),
(193,	64,	'25.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\25.csv'),
(194,	65,	'26.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\26.csv'),
(195,	66,	'27.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\27.csv'),
(196,	67,	'28.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\28.csv'),
(197,	68,	'29.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\29.csv'),
(198,	69,	'30.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\30.csv'),
(199,	70,	'31.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\31.csv'),
(200,	71,	'32.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\32.csv'),
(201,	72,	'33.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\33.csv'),
(202,	73,	'34.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\34.csv'),
(203,	74,	'35.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\35.csv'),
(204,	75,	'36.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\36.csv'),
(205,	76,	'37.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\37.csv'),
(206,	77,	'38.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\38.csv'),
(207,	78,	'39.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\39.csv'),
(208,	79,	'4.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\4.csv'),
(209,	80,	'40.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\40.csv'),
(210,	81,	'41.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\41.csv'),
(211,	82,	'42.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\42.csv'),
(212,	83,	'43.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\43.csv'),
(213,	84,	'44.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\44.csv'),
(214,	85,	'45.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\45.csv'),
(215,	86,	'46.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\46.csv'),
(216,	87,	'47.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\47.csv'),
(217,	88,	'48.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\48.csv'),
(218,	89,	'49.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\49.csv'),
(219,	90,	'5.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\5.csv'),
(220,	91,	'50.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\50.csv'),
(221,	92,	'51.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\51.csv'),
(222,	93,	'53.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\53.csv'),
(223,	94,	'54.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\54.csv'),
(224,	95,	'55.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\55.csv'),
(225,	96,	'56.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\56.csv'),
(226,	97,	'58.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\58.csv'),
(227,	98,	'59.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\59.csv'),
(228,	99,	'6.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\6.csv'),
(229,	100,	'60.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\60.csv'),
(230,	101,	'61.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\61.csv'),
(231,	102,	'62.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\62.csv'),
(232,	103,	'64.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\64.csv'),
(233,	104,	'65.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\65.csv'),
(234,	105,	'66.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\66.csv'),
(235,	106,	'67.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\67.csv'),
(236,	107,	'68.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\68.csv'),
(237,	108,	'69.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\69.csv'),
(238,	109,	'7.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\7.csv'),
(239,	110,	'70.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\70.csv'),
(240,	111,	'71.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\71.csv'),
(241,	112,	'72.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\72.csv'),
(242,	113,	'73.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\73.csv'),
(243,	114,	'74.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\74.csv'),
(244,	115,	'75.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\75.csv'),
(245,	116,	'76.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\76.csv'),
(246,	117,	'77.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\77.csv'),
(247,	118,	'78.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\78.csv'),
(248,	119,	'79.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\79.csv'),
(249,	120,	'8.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\8.csv'),
(250,	121,	'80.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\80.csv'),
(251,	122,	'81.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\81.csv'),
(252,	123,	'82.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\82.csv'),
(253,	124,	'83.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\83.csv'),
(254,	125,	'84.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\84.csv'),
(255,	126,	'85.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\85.csv'),
(256,	127,	'86.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\86.csv'),
(257,	128,	'87.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\87.csv'),
(258,	129,	'88.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\88.csv'),
(259,	130,	'89.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\89.csv'),
(260,	131,	'9.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\9.csv'),
(261,	132,	'90.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\90.csv'),
(262,	133,	'92.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\92.csv'),
(263,	134,	'93.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\93.csv'),
(264,	135,	'94.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\94.csv'),
(265,	136,	'95.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\95.csv'),
(266,	137,	'96.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\96.csv'),
(267,	138,	'97.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\97.csv'),
(268,	139,	'98.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\98.csv'),
(269,	140,	'99.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\99.csv'),
(270,	141,	'korrek.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\korrek.csv'),
(271,	142,	'log.txt',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\log.txt'),
(272,	143,	'M1.2.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\M1.2.csv'),
(273,	144,	'M1.3.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\M1.3.csv'),
(274,	145,	'M2.1.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\M2.1.csv'),
(275,	146,	'M2.2.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\M2.2.csv'),
(276,	147,	'M3.1.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\M3.1.csv'),
(277,	148,	'M3.2.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\M3.2.csv'),
(278,	149,	'M4.1.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\M4.1.csv'),
(279,	150,	'M5.1.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\M5.1.csv'),
(280,	151,	'M5.2.csv',	31,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\csv\\M5.2.csv'),
(281,	152,	'functions_for_DC.R',	30,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\functions_for_DC.R'),
(282,	153,	'functions_for_visualization.R',	30,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\functions_for_visualization.R'),
(283,	154,	'hydraulic_func.R',	30,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\hydraulic_func.R'),
(284,	155,	'Input',	30,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\Input'),
(285,	156,	'Diss_michael_anlage.csv',	155,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\Input\\Diss_michael_anlage.csv'),
(286,	157,	'michael_rough_annex2.csv',	155,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\Input\\michael_rough_annex2.csv'),
(287,	158,	'readme_Diss_michael_anlage.txt',	155,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\Input\\readme_Diss_michael_anlage.txt'),
(288,	159,	'remarks_on_AnneRuns.txt',	155,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\Input\\remarks_on_AnneRuns.txt'),
(289,	160,	'process',	30,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\process'),
(290,	161,	'ready2.csv',	30,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\ready2.csv'),
(291,	162,	'readytime.csv',	30,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\readytime.csv'),
(292,	163,	'single_file.R',	30,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database\\single_file.R'),
(293,	164,	'database2',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database2'),
(294,	165,	'CALCall.txt',	164,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database2\\CALCall.txt'),
(295,	166,	'Datensatz2.Rmd',	164,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database2\\Datensatz2.Rmd'),
(296,	167,	'derivedparams.csv',	164,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database2\\derivedparams.csv'),
(297,	168,	'HOR.txt',	164,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database2\\HOR.txt'),
(298,	169,	'Macropore.txt',	164,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database2\\Macropore.txt'),
(299,	170,	'prep.R',	164,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database2\\prep.R'),
(300,	171,	'RUNPROPall.txt',	164,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database2\\RUNPROPall.txt'),
(301,	172,	'RUNTEMP.txt',	164,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database2\\RUNTEMP.txt'),
(302,	173,	'SOILall.txt',	164,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\database2\\SOILall.txt'),
(303,	174,	'export',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\export'),
(304,	175,	'meta.csv',	174,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\export\\meta.csv'),
(305,	176,	'time.csv',	174,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\export\\time.csv'),
(306,	177,	'index.Rmd',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\index.Rmd'),
(307,	178,	'para_opti',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\para_opti'),
(308,	179,	'by_R',	178,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\para_opti\\by_R'),
(309,	180,	'aMC_in_R.R',	179,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\aMC_in_R.R'),
(310,	181,	'aMC_in_R_ewid.R',	179,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\aMC_in_R_ewid.R'),
(311,	182,	'avisualization.R',	179,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\avisualization.R'),
(312,	183,	'avisualization2.R',	179,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\avisualization2.R'),
(313,	184,	'preamble.tex',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\preamble.tex'),
(314,	185,	'_output.yml',	7,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\lenz2022_zip\\lenz2022\\_output.yml'),
(315,	186,	'09-database.Rmd',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\09-database.Rmd'),
(316,	187,	'11-varrain.Rmd',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\11-varrain.Rmd'),
(317,	188,	'08-E3DIssues.Rmd',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\08-E3DIssues.Rmd'),
(318,	189,	'_output.yml',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\_output.yml'),
(319,	190,	'07-references.Rmd',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\07-references.Rmd'),
(320,	191,	'preamble.tex',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\preamble.tex'),
(321,	192,	'03a-code.Rmd',	NULL,	172,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\172\\03a-code.Rmd');

CREATE TABLE `datasets` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_local` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `resource_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `resource_id` (`resource_id`),
  CONSTRAINT `datasets_ibfk_1` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON DELETE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;


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


CREATE TABLE `mappings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  `resource_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `resource_id` (`resource_id`),
  CONSTRAINT `mappings_ibfk_1` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='stores relations between metadata entity mappings and resources';


CREATE TABLE `resources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `doi` varchar(255) NOT NULL,
  `files_stored` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='stores information about resources';

INSERT INTO `resources` (`id`, `name`, `doi`, `files_stored`) VALUES
(171,	'Michael Schmuker\'s neuromorphic_classifiers',	'10.5281/zenodo.18726',	1),
(172,	'Jonas Lenz\'s dissertation package',	'10.5281/zenodo.6654150',	1);

CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

INSERT INTO `users` (`id`, `username`, `first_name`, `last_name`) VALUES
(1,	'devatjan',	'Jan',	'Devátý');

CREATE TABLE `user_resource` (
  `user_id` int(11) NOT NULL,
  `resource_id` int(11) NOT NULL,
  KEY `user_id` (`user_id`),
  KEY `resource_id` (`resource_id`),
  CONSTRAINT `user_resource_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE NO ACTION,
  CONSTRAINT `user_resource_ibfk_2` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

INSERT INTO `user_resource` (`user_id`, `resource_id`) VALUES
(1,	171),
(1,	172);

-- 2024-06-25 05:39:21
