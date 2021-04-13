-- Adminer 4.8.0 MySQL 5.5.5-10.4.13-MariaDB dump

DROP TABLE IF EXISTS `foto`;
CREATE TABLE `foto` (
  `pid` int(11) NOT NULL,
  `url` tinytext NOT NULL,
  PRIMARY KEY (`pid`,`url`),
  CONSTRAINT `foto_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `produto` (`pid`)
);

INSERT INTO `foto` (`pid`, `url`) VALUES
(0,	'/static/img/user-content/chrome-icon.png'),
(0,	'https://s2.glbimg.com/stcmYhm5538wMFuDgDAv56N3HiA=/1200x/smart/filters:cover():strip_icc()/i.s3.glbimg.com/v1/AUTH_f035dd6fd91c438fa04ab718d608bbaa/internal_photos/bs/2019/u/8/JoFHTBS3aJRvZvuVjaFw/magalu.jpg'),
(0,	'https://yt3.ggpht.com/ytc/AAUvwnjB3j_goCXArrixpBnluCM7H1nQW38EF_MBPhk8uxc=s900-c-k-c0x00ffffff-no-rj'),
(1,	'https://www.oficinadanet.com.br/imagens/post/24973/pc-gamer.jpg'),
(2,	'https://media-exp1.licdn.com/dms/image/C4D03AQGIt868arB2QQ/profile-displayphoto-shrink_200_200/0/1585182495544?e=1622073600&v=beta&t=zagMzAcbFBkmm42kCMkyvyC-yy14CXFtm7h7HblGXP0'),
(3,	'https://media.gazetadopovo.com.br/2019/10/17181228/marijuana-1556358-372x372.jpg'),
(4,	'https://nintendoboysite.files.wordpress.com/2017/09/ash-pikachu.jpg'),
(5,	'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Mallard2.jpg/1200px-Mallard2.jpg'),
(6,	'/static/img/user-content/gerardo-crop.jpeg'),
(6,	'/static/img/user-content/patchesdks3.png'),
(7,	'https://s3.amazonaws.com/paranavai.portaldacidade.com/img/news/2019-05/voluntarios-constroem-casa-para-familia-que-morava-em-barraco-na-vila-alta-5cd5e6b6260fd.jpeg'),
(8,	'https://ufmg.br/thumbor/XsLSCicvWZuHvyued9G3SaiOx30=/0x22:2282x1547/712x474/https://ufmg.br/storage/c/9/9/5/c99595fb0ed0b72fa199832e808c7871_15192185516154_490857661.jpeg'),
(9,	'https://pbs.twimg.com/media/C-QnjEJWsAEe-kk.jpg'),
(10,	'/static/img/brenno.png');

DROP TABLE IF EXISTS `historico`;
CREATE TABLE `historico` (
  `pid` int(11) NOT NULL,
  `cid` int(11) NOT NULL,
  `fid` int(11) NOT NULL,
  `data` datetime NOT NULL,
  `qtd` int(11) DEFAULT NULL,
  `total` double DEFAULT NULL,
  PRIMARY KEY (`pid`,`cid`,`fid`,`data`),
  CONSTRAINT `historico_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `produto` (`pid`),
  CONSTRAINT `historico_ibfk_2` FOREIGN KEY (`cid`) REFERENCES `pessoa` (`uid`),
  CONSTRAINT `historico_ibfk_3` FOREIGN KEY (`fid`) REFERENCES `pessoa` (`uid`)
);

INSERT INTO `historico` (`pid`, `cid`, `fid`, `data`, `qtd`, `total`) VALUES
(0,	1,	0,	'2021-04-11 22:50:39',	1,	400),
(0,	1,	0,	'2021-04-11 23:11:45',	1,	400),
(0,	3,	0,	'2021-04-13 04:09:01',	5,	2000),
(1,	1,	0,	'2021-04-11 22:50:39',	1,	456465),
(2,	1,	0,	'2021-04-11 22:50:39',	1,	25),
(3,	1,	0,	'2021-04-11 22:50:39',	1,	59),
(4,	1,	0,	'2021-04-11 22:50:39',	1,	240),
(5,	1,	0,	'2021-04-11 22:50:39',	1,	154),
(6,	1,	0,	'2021-04-11 22:50:39',	1,	5.5),
(7,	1,	0,	'2021-04-11 22:50:39',	1,	1525000),
(8,	1,	0,	'2021-04-11 22:50:39',	1,	0),
(9,	1,	0,	'2021-04-11 22:50:39',	1,	892),
(10,	1,	0,	'2021-04-11 22:50:39',	1,	3.1);

DROP TABLE IF EXISTS `pessoa`;
CREATE TABLE `pessoa` (
  `uid` int(11) NOT NULL,
  `nome` varchar(20) DEFAULT NULL,
  `email` varchar(40) DEFAULT NULL,
  `senha` varchar(20) DEFAULT NULL,
  `tipo` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`uid`)
);

INSERT INTO `pessoa` (`uid`, `nome`, `email`, `senha`, `tipo`) VALUES
(0,	'bolatron',	'bola@tron',	'pokemon',	1),
(1,	'ana',	'ana@clara',	'clara',	1),
(2,	'campinas',	'lucas@campin.as',	'bolacha',	1),
(3,	'brenno',	'asd@asd',	'asd',	2),
(4,	'keina',	'ddd@ddd',	't',	2),
(5,	'benks',	'benks@onlyfans',	'loli',	2);

DROP TABLE IF EXISTS `possui_no_carrinho`;
CREATE TABLE `possui_no_carrinho` (
  `pid` int(11) NOT NULL,
  `cid` int(11) NOT NULL,
  `qtd` int(11) DEFAULT NULL,
  PRIMARY KEY (`pid`,`cid`),
  CONSTRAINT `possui_no_carrinho_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `produto` (`pid`),
  CONSTRAINT `possui_no_carrinho_ibfk_2` FOREIGN KEY (`cid`) REFERENCES `pessoa` (`uid`)
);

INSERT INTO `possui_no_carrinho` (`pid`, `cid`, `qtd`) VALUES
(0,	3,	3),
(2,	3,	2),
(3,	3,	15),
(5,	3,	1);

DROP TABLE IF EXISTS `produto`;
CREATE TABLE `produto` (
  `pid` int(11) NOT NULL,
  `fid` int(11) NOT NULL,
  `nome` varchar(40) DEFAULT NULL,
  `descricao` text DEFAULT NULL,
  `capa` tinytext DEFAULT NULL,
  `qtd` int(11) DEFAULT NULL,
  `valor` double DEFAULT NULL,
  `vendas` int(11) DEFAULT NULL,
  PRIMARY KEY (`pid`,`fid`),
  CONSTRAINT `produto_ibfk_2` FOREIGN KEY (`fid`) REFERENCES `pessoa` (`uid`) ON DELETE CASCADE
);

INSERT INTO `produto` (`pid`, `fid`, `nome`, `descricao`, `capa`, `qtd`, `valor`, `vendas`) VALUES
(0,	0,	'Boneca inflável MagaLu',	'Vocês pediram, a gente entrega! Se divirta com a nova boneca inflável da MagaLu! Agora ela emite sons ao chacoalhar.',	'https://yt3.ggpht.com/ytc/AAUvwnjB3j_goCXArrixpBnluCM7H1nQW38EF_MBPhk8uxc=s900-c-k-c0x00ffffff-no-rj',	7,	400,	0),
(1,	0,	'PC Gamer do Safadão',	'É o PC gamer do safadão!!!!',	'https://www.oficinadanet.com.br/imagens/post/24973/pc-gamer.jpg',	200,	456465,	2),
(2,	0,	'CD Autografado pelo Safadão',	'Isso mesmo, o próprio Weslley vulgo Safadão autografará seu trigésimo CD da porra do sertanejo universitário.',	'https://media-exp1.licdn.com/dms/image/C4D03AQGIt868arB2QQ/profile-displayphoto-shrink_200_200/0/1585182495544?e=1622073600&v=beta&t=zagMzAcbFBkmm42kCMkyvyC-yy14CXFtm7h7HblGXP0',	28,	25,	4),
(3,	0,	'Maconha',	'ervinha danada',	'https://media.gazetadopovo.com.br/2019/10/17181228/marijuana-1556358-372x372.jpg',	-14,	59,	0),
(4,	0,	'Bolatrons Pikachu',	'Perfeito para rinha de animal ilegal!\r\n\r\nGaranta o seu já',	'https://nintendoboysite.files.wordpress.com/2017/09/ash-pikachu.jpg',	200,	240,	5),
(5,	0,	'Pato de Para de Minas',	'Pato roubado da praça de Para de Minas',	'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Mallard2.jpg/1200px-Mallard2.jpg',	57,	154,	10),
(6,	0,	'Cadeira Gamer Raiz',	'Para aquele que entende o valor de um dólar. atualizada',	'https://lh3.googleusercontent.com/proxy/HN5L9qH9kEoZlZyd8aAyGHCF146xvgeK7joWHWr_SdKN4WESVh77ZXp8DlyJW_hkQcHpem3aRgwpb7vWHqFIjhdzTyBzgkr7mxdAik4TnzU-6JCZAzQJXnKHGADOH1w6XKD0GMdnbAQDtxy-Owdl6GcNgjw',	200,	5.5,	300),
(7,	0,	'Sitio do Leo',	'Sitio que o Leo quer se livrar',	'https://s3.amazonaws.com/paranavai.portaldacidade.com/img/news/2019-05/voluntarios-constroem-casa-para-familia-que-morava-em-barraco-na-vila-alta-5cd5e6b6260fd.jpeg',	200,	1525000,	0),
(8,	0,	'Revolução comunista',	'Já tava na hora',	'https://ufmg.br/thumbor/XsLSCicvWZuHvyued9G3SaiOx30=/0x22:2282x1547/712x474/https://ufmg.br/storage/c/9/9/5/c99595fb0ed0b72fa199832e808c7871_15192185516154_490857661.jpeg',	200,	0,	0),
(9,	0,	'Cerebro de Web Developer',	'pra vc que é burrinho',	'https://pbs.twimg.com/media/C-QnjEJWsAEe-kk.jpg',	200,	892,	22),
(10,	0,	'Web Developer Profissional',	'Tá surpreso?',	'/static/img/brenno.png',	200,	3.1,	1000);