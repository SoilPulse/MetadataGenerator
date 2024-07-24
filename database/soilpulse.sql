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
  `content` varchar(2047) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `parent_id` (`parent_id_local`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `containers_ibfk_4` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

INSERT INTO `containers` (`id`, `id_local`, `name`, `type`, `parent_id_local`, `project_id`, `path`, `content`) VALUES
(1,	1,	'DOI metadata',	'json',	NULL,	1,	NULL,	'{\'data\': {\'id\': \'10.5281/zenodo.6654150\', \'type\': \'dois\', \'attributes\': {\'doi\': \'10.5281/zenodo.6654150\', \'prefix\': \'10.5281\', \'suffix\': \'zenodo.6654150\', \'identifiers\': [], \'alternateIdentifiers\': [], \'creators\': [{\'name\': \'Lenz, Jonas\', \'givenName\': \'Jonas\', \'familyName\': \'Lenz\', \'affiliation\': [\'TU Bergakademie Freiberg\'], \'nameIdentifiers\': [{\'schemeUri\': \'https://orcid.org\', \'nameIdentifier\': \'https://orcid.org/0000-0002-6167-1161\', \'nameIdentifierScheme\': \'ORCID\'}]}], \'titles\': [{\'title\': \'PHD-dissertation-code: \"Improved parameter estimation for the soil erosion modeling tool EROSION-3D\"\'}], \'publisher\': \'Zenodo\', \'container\': {}, \'publicationYear\': 2022, \'subjects\': [{\'subject\': \'soil erosion modeling; EROSION-3D\'}], \'contributors\': [], \'dates\': [{\'date\': \'2022-07-20\', \'dateType\': \'Issued\'}], \'language\': \'en\', \'types\': {\'ris\': \'RPRT\', \'bibtex\': \'article\', \'citeproc\': \'article-journal\', \'schemaOrg\': \'ScholarlyArticle\', \'resourceType\': \'Thesis\', \'resourceTypeGeneral\': \'Text\'}, \'relatedIdentifiers\': [{\'relationType\': \'IsVersionOf\', \'relatedIdentifier\': \'10.5281/zenodo.6654149\', \'relatedIdentifierType\': \'DOI\'}], \'relatedItems\': [], \'sizes\': [], \'formats\': [], \'version\': \'0.9 - state of submission\', \'rightsList\': [{\'rights\': \'Creative Commons Attribution 4.0 International\', \'rightsUri\': \'https://creativecommons.org/licenses/by/4.0/legalcode\', \'schemeUri\': \'https://spdx.org/licenses/\', \'rightsIdentifier\': \'cc-by-4.0\', \'rightsIdentifierScheme\': \'SPDX\'}, {\'rights\': \'Open Access\', \'rightsUri\': \'info:eu-repo/semantics/openAccess\'}], \'descriptions\': [{\'description\': \'Source code to the dissertation project \"Improved parameter estimation for the soil erosion modeling tool EROSION-3D\" This repo contains the *.Rmd source files of my thesis project, the included source code used for data analysis and processing; and the primary data compiled from different base repositories for this thesis. Style files (e.g. citation, latex template), protected third party software, citation information (*.bib files) and data of the ba'),
(2,	2,	'Publisher metadata',	'json',	NULL,	1,	NULL,	'{\'created\': \'2022-07-18T19:49:11.999235+00:00\', \'modified\': \'2022-07-19T01:49:45.155967+00:00\', \'id\': 6654150, \'conceptrecid\': \'6654149\', \'doi\': \'10.5281/zenodo.6654150\', \'conceptdoi\': \'10.5281/zenodo.6654149\', \'doi_url\': \'https://doi.org/10.5281/zenodo.6654150\', \'metadata\': {\'title\': \'PHD-dissertation-code: \"Improved parameter estimation for the soil erosion modeling tool EROSION-3D\"\', \'doi\': \'10.5281/zenodo.6654150\', \'publication_date\': \'2022-07-20\', \'description\': \'<p>Source code to the dissertation project &quot;Improved parameter estimation for the soil erosion modeling tool EROSION-3D&quot;</p>\\n\\n<p>This repo contains the *.Rmd source files of my thesis project, the included source code used for data analysis and processing; and the primary data compiled from different base repositories for this thesis. Style files (e.g. citation, latex template), protected third party software, citation information (*.bib files) and data of the base repositories is available from the author upon request.</p>\', \'access_right\': \'open\', \'creators\': [{\'name\': \'Lenz, Jonas\', \'affiliation\': \'TU Bergakademie Freiberg\', \'orcid\': \'0000-0002-6167-1161\'}], \'keywords\': [\'soil erosion modeling; EROSION-3D\'], \'version\': \'0.9 - state of submission\', \'language\': \'eng\', \'resource_type\': {\'title\': \'Thesis\', \'type\': \'publication\', \'subtype\': \'thesis\'}, \'license\': {\'id\': \'cc-by-4.0\'}, \'relations\': {\'version\': [{\'index\': 0, \'is_last\': True, \'parent\': {\'pid_type\': \'recid\', \'pid_value\': \'6654149\'}}]}}, \'title\': \'PHD-dissertation-code: \"Improved parameter estimation for the soil erosion modeling tool EROSION-3D\"\', \'links\': {\'self\': \'https://zenodo.org/api/records/6654150\', \'self_html\': \'https://zenodo.org/records/6654150\', \'self_doi\': \'https://zenodo.org/doi/10.5281/zenodo.6654150\', \'doi\': \'https://doi.org/10.5281/zenodo.6654150\', \'parent\': \'https://zenodo.org/api/records/6654149\', \'parent_html\': \'https://zenodo.org/records/6654149\', \'parent_doi\': \'https://zenodo.org/doi/10.5281/zenodo.6654149\', \'self_iiif_manifest\': \'https://zenodo.org/api/iii'),
(3,	3,	'10-toolboxvignette.Rmd',	'file',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\10-toolboxvignette.Rmd',	'None'),
(4,	4,	'06-lookout.Rmd',	'file',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\06-lookout.Rmd',	'None'),
(5,	5,	'index.Rmd',	'file',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\index.Rmd',	'None'),
(6,	6,	'lenz2022.zip',	'archive',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip',	'None'),
(7,	7,	'lenz2022',	'directory',	6,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022',	'None'),
(8,	8,	'01-intro.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\01-intro.Rmd',	'None'),
(9,	9,	'02-state_know.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\02-state_know.Rmd',	'None'),
(10,	10,	'03-database.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\03-database.Rmd',	'None'),
(11,	11,	'03a-code.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\03a-code.Rmd',	'None'),
(12,	12,	'04-results.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\04-results.Rmd',	'None'),
(13,	13,	'04a-results_PO.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\04a-results_PO.Rmd',	'None'),
(14,	14,	'04b-results-statis.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\04b-results-statis.Rmd',	'None'),
(15,	15,	'05-discussion.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\05-discussion.Rmd',	'None'),
(16,	16,	'05a-reallookout.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\05a-reallookout.Rmd',	'None'),
(17,	17,	'06-lookout.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\06-lookout.Rmd',	'None'),
(18,	18,	'07-references.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\07-references.Rmd',	'None'),
(19,	19,	'08-E3DIssues.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\08-E3DIssues.Rmd',	'None'),
(20,	20,	'09-database.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\09-database.Rmd',	'None'),
(21,	21,	'10-toolboxvignette.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\10-toolboxvignette.Rmd',	'None'),
(22,	22,	'11-varrain.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\11-varrain.Rmd',	'None'),
(23,	23,	'comp_infils',	'directory',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils',	'None'),
(24,	24,	'comp_E3D_landlab.Rmd',	'file',	23,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\comp_E3D_landlab.Rmd',	'None'),
(25,	25,	'comp_infil.R',	'file',	23,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\comp_infil.R',	'None'),
(26,	26,	'implicite_GA.R',	'file',	23,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\implicite_GA.R',	'None'),
(27,	27,	'py',	'directory',	23,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\py',	'None'),
(28,	28,	'GA_comparison.ipynb',	'file',	27,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\py\\GA_comparison.ipynb',	'None'),
(29,	29,	'GA_results.csv',	'file',	27,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\comp_infils\\py\\GA_results.csv',	'None'),
(30,	30,	'database',	'directory',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database',	'None'),
(31,	31,	'csv',	'directory',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv',	'None'),
(32,	32,	'1.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\1.csv',	'None'),
(33,	33,	'10.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\10.csv',	'None'),
(34,	34,	'100.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\100.csv',	'None'),
(35,	35,	'101.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\101.csv',	'None'),
(36,	36,	'102.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\102.csv',	'None'),
(37,	37,	'104.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\104.csv',	'None'),
(38,	38,	'105.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\105.csv',	'None'),
(39,	39,	'106.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\106.csv',	'None'),
(40,	40,	'107.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\107.csv',	'None'),
(41,	41,	'108.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\108.csv',	'None'),
(42,	42,	'109.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\109.csv',	'None'),
(43,	43,	'11.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\11.csv',	'None'),
(44,	44,	'110.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\110.csv',	'None'),
(45,	45,	'111.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\111.csv',	'None'),
(46,	46,	'112.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\112.csv',	'None'),
(47,	47,	'114.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\114.csv',	'None'),
(48,	48,	'115.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\115.csv',	'None'),
(49,	49,	'116.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\116.csv',	'None'),
(50,	50,	'12.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\12.csv',	'None'),
(51,	51,	'13.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\13.csv',	'None'),
(52,	52,	'14.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\14.csv',	'None'),
(53,	53,	'15.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\15.csv',	'None'),
(54,	54,	'16.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\16.csv',	'None'),
(55,	55,	'17.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\17.csv',	'None'),
(56,	56,	'18.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\18.csv',	'None'),
(57,	57,	'19.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\19.csv',	'None'),
(58,	58,	'2.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\2.csv',	'None'),
(59,	59,	'20.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\20.csv',	'None'),
(60,	60,	'21.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\21.csv',	'None'),
(61,	61,	'22.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\22.csv',	'None'),
(62,	62,	'23.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\23.csv',	'None'),
(63,	63,	'24.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\24.csv',	'None'),
(64,	64,	'25.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\25.csv',	'None'),
(65,	65,	'26.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\26.csv',	'None'),
(66,	66,	'27.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\27.csv',	'None'),
(67,	67,	'28.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\28.csv',	'None'),
(68,	68,	'29.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\29.csv',	'None'),
(69,	69,	'30.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\30.csv',	'None'),
(70,	70,	'31.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\31.csv',	'None'),
(71,	71,	'32.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\32.csv',	'None'),
(72,	72,	'33.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\33.csv',	'None'),
(73,	73,	'34.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\34.csv',	'None'),
(74,	74,	'35.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\35.csv',	'None'),
(75,	75,	'36.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\36.csv',	'None'),
(76,	76,	'37.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\37.csv',	'None'),
(77,	77,	'38.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\38.csv',	'None'),
(78,	78,	'39.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\39.csv',	'None'),
(79,	79,	'4.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\4.csv',	'None'),
(80,	80,	'40.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\40.csv',	'None'),
(81,	81,	'41.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\41.csv',	'None'),
(82,	82,	'42.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\42.csv',	'None'),
(83,	83,	'43.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\43.csv',	'None'),
(84,	84,	'44.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\44.csv',	'None'),
(85,	85,	'45.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\45.csv',	'None'),
(86,	86,	'46.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\46.csv',	'None'),
(87,	87,	'47.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\47.csv',	'None'),
(88,	88,	'48.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\48.csv',	'None'),
(89,	89,	'49.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\49.csv',	'None'),
(90,	90,	'5.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\5.csv',	'None'),
(91,	91,	'50.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\50.csv',	'None'),
(92,	92,	'51.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\51.csv',	'None'),
(93,	93,	'53.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\53.csv',	'None'),
(94,	94,	'54.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\54.csv',	'None'),
(95,	95,	'55.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\55.csv',	'None'),
(96,	96,	'56.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\56.csv',	'None'),
(97,	97,	'58.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\58.csv',	'None'),
(98,	98,	'59.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\59.csv',	'None'),
(99,	99,	'6.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\6.csv',	'None'),
(100,	100,	'60.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\60.csv',	'None'),
(101,	101,	'61.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\61.csv',	'None'),
(102,	102,	'62.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\62.csv',	'None'),
(103,	103,	'64.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\64.csv',	'None'),
(104,	104,	'65.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\65.csv',	'None'),
(105,	105,	'66.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\66.csv',	'None'),
(106,	106,	'67.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\67.csv',	'None'),
(107,	107,	'68.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\68.csv',	'None'),
(108,	108,	'69.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\69.csv',	'None'),
(109,	109,	'7.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\7.csv',	'None'),
(110,	110,	'70.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\70.csv',	'None'),
(111,	111,	'71.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\71.csv',	'None'),
(112,	112,	'72.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\72.csv',	'None'),
(113,	113,	'73.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\73.csv',	'None'),
(114,	114,	'74.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\74.csv',	'None'),
(115,	115,	'75.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\75.csv',	'None'),
(116,	116,	'76.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\76.csv',	'None'),
(117,	117,	'77.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\77.csv',	'None'),
(118,	118,	'78.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\78.csv',	'None'),
(119,	119,	'79.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\79.csv',	'None'),
(120,	120,	'8.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\8.csv',	'None'),
(121,	121,	'80.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\80.csv',	'None'),
(122,	122,	'81.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\81.csv',	'None'),
(123,	123,	'82.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\82.csv',	'None'),
(124,	124,	'83.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\83.csv',	'None'),
(125,	125,	'84.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\84.csv',	'None'),
(126,	126,	'85.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\85.csv',	'None'),
(127,	127,	'86.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\86.csv',	'None'),
(128,	128,	'87.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\87.csv',	'None'),
(129,	129,	'88.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\88.csv',	'None'),
(130,	130,	'89.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\89.csv',	'None'),
(131,	131,	'9.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\9.csv',	'None'),
(132,	132,	'90.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\90.csv',	'None'),
(133,	133,	'92.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\92.csv',	'None'),
(134,	134,	'93.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\93.csv',	'None'),
(135,	135,	'94.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\94.csv',	'None'),
(136,	136,	'95.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\95.csv',	'None'),
(137,	137,	'96.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\96.csv',	'None'),
(138,	138,	'97.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\97.csv',	'None'),
(139,	139,	'98.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\98.csv',	'None'),
(140,	140,	'99.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\99.csv',	'None'),
(141,	141,	'korrek.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\korrek.csv',	'None'),
(142,	142,	'log.txt',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\log.txt',	'None'),
(143,	143,	'M1.2.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M1.2.csv',	'None'),
(144,	144,	'M1.3.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M1.3.csv',	'None'),
(145,	145,	'M2.1.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M2.1.csv',	'None'),
(146,	146,	'M2.2.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M2.2.csv',	'None'),
(147,	147,	'M3.1.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M3.1.csv',	'None'),
(148,	148,	'M3.2.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M3.2.csv',	'None'),
(149,	149,	'M4.1.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M4.1.csv',	'None'),
(150,	150,	'M5.1.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M5.1.csv',	'None'),
(151,	151,	'M5.2.csv',	'file',	31,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\csv\\M5.2.csv',	'None'),
(152,	152,	'functions_for_DC.R',	'file',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\functions_for_DC.R',	'None'),
(153,	153,	'functions_for_visualization.R',	'file',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\functions_for_visualization.R',	'None'),
(154,	154,	'hydraulic_func.R',	'file',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\hydraulic_func.R',	'None'),
(155,	155,	'Input',	'directory',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\Input',	'None'),
(156,	156,	'Diss_michael_anlage.csv',	'file',	155,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\Input\\Diss_michael_anlage.csv',	'None'),
(157,	157,	'michael_rough_annex2.csv',	'file',	155,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\Input\\michael_rough_annex2.csv',	'None'),
(158,	158,	'readme_Diss_michael_anlage.txt',	'file',	155,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\Input\\readme_Diss_michael_anlage.txt',	'None'),
(159,	159,	'remarks_on_AnneRuns.txt',	'file',	155,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\Input\\remarks_on_AnneRuns.txt',	'None'),
(160,	160,	'process',	'directory',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\process',	'None'),
(161,	161,	'ready2.csv',	'file',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\ready2.csv',	'None'),
(162,	162,	'readytime.csv',	'file',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\readytime.csv',	'None'),
(163,	163,	'single_file.R',	'file',	30,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database\\single_file.R',	'None'),
(164,	164,	'database2',	'directory',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2',	'None'),
(165,	165,	'CALCall.txt',	'file',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\CALCall.txt',	'None'),
(166,	166,	'Datensatz2.Rmd',	'file',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\Datensatz2.Rmd',	'None'),
(167,	167,	'derivedparams.csv',	'file',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\derivedparams.csv',	'None'),
(168,	168,	'HOR.txt',	'file',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\HOR.txt',	'None'),
(169,	169,	'Macropore.txt',	'file',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\Macropore.txt',	'None'),
(170,	170,	'prep.R',	'file',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\prep.R',	'None'),
(171,	171,	'RUNPROPall.txt',	'file',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\RUNPROPall.txt',	'None'),
(172,	172,	'RUNTEMP.txt',	'file',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\RUNTEMP.txt',	'None'),
(173,	173,	'SOILall.txt',	'file',	164,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\database2\\SOILall.txt',	'None'),
(174,	174,	'export',	'directory',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\export',	'None'),
(175,	175,	'meta.csv',	'file',	174,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\export\\meta.csv',	'None'),
(176,	176,	'time.csv',	'file',	174,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\export\\time.csv',	'None'),
(177,	177,	'index.Rmd',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\index.Rmd',	'None'),
(178,	178,	'para_opti',	'directory',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti',	'None'),
(179,	179,	'by_R',	'directory',	178,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti\\by_R',	'None'),
(180,	180,	'aMC_in_R.R',	'file',	179,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\aMC_in_R.R',	'None'),
(181,	181,	'aMC_in_R_ewid.R',	'file',	179,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\aMC_in_R_ewid.R',	'None'),
(182,	182,	'avisualization.R',	'file',	179,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\avisualization.R',	'None'),
(183,	183,	'avisualization2.R',	'file',	179,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\para_opti\\by_R\\avisualization2.R',	'None'),
(184,	184,	'preamble.tex',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\preamble.tex',	'None'),
(185,	185,	'_output.yml',	'file',	7,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\lenz2022_zip\\lenz2022\\_output.yml',	'None'),
(186,	186,	'09-database.Rmd',	'file',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\09-database.Rmd',	'None'),
(187,	187,	'11-varrain.Rmd',	'file',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\11-varrain.Rmd',	'None'),
(188,	188,	'08-E3DIssues.Rmd',	'file',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\08-E3DIssues.Rmd',	'None'),
(189,	189,	'_output.yml',	'file',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\_output.yml',	'None'),
(190,	190,	'07-references.Rmd',	'file',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\07-references.Rmd',	'None'),
(191,	191,	'preamble.tex',	'file',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\preamble.tex',	'None'),
(192,	192,	'03a-code.Rmd',	'file',	NULL,	1,	'D:\\Dokumenty\\SoilPulse\\MetadataGenerator\\downloaded_files\\1\\03a-code.Rmd',	'None');

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

-- 2024-07-09 11:39:11
