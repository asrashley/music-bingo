PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Directory" (
  "pk" INTEGER PRIMARY KEY AUTOINCREMENT,
  "name" TEXT UNIQUE NOT NULL,
  "title" TEXT NOT NULL,
  "artist" TEXT NOT NULL,
  "directory" INTEGER REFERENCES "Directory" ("pk") ON DELETE SET NULL
);
INSERT INTO Directory VALUES(1,'Clips/TV Themes','[TV Themes]','',NULL);
CREATE TABLE IF NOT EXISTS "Game" (
  "pk" INTEGER PRIMARY KEY AUTOINCREMENT,
  "id" VARCHAR(64) UNIQUE NOT NULL,
  "title" TEXT NOT NULL,
  "start" DATETIME UNIQUE NOT NULL,
  "end" DATETIME NOT NULL
);
INSERT INTO Game VALUES(5,'20-04-24-2','TV Themes','2020-04-24 18:05:44.048300','2020-08-02 18:05:44.048300');
CREATE TABLE IF NOT EXISTS "Song" (
  "pk" INTEGER PRIMARY KEY AUTOINCREMENT,
  "directory" INTEGER NOT NULL REFERENCES "Directory" ("pk") ON DELETE CASCADE,
  "filename" TEXT NOT NULL,
  "title" TEXT NOT NULL,
  "artist" TEXT NOT NULL,
  "duration" INTEGER UNSIGNED NOT NULL,
  "channels" INTEGER UNSIGNED NOT NULL,
  "sample_rate" INTEGER UNSIGNED NOT NULL,
  "sample_width" INTEGER UNSIGNED NOT NULL,
  "bitrate" INTEGER UNSIGNED NOT NULL,
  "album" TEXT NOT NULL,
  CONSTRAINT "unq_song__directory_filename" UNIQUE ("directory", "filename")
);
INSERT INTO Song VALUES(1,1,'01-25- Ghostbusters.mp3','Ghostbusters','Ray Parker Jr',30016,2,44100,16,256,'100 Hits 80s Essentials');
INSERT INTO Song VALUES(2,1,'02 Match Of The Day.mp3','Match Of The Day','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(3,1,'02 Sex And The City.mp3','Sex And The City','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(4,1,'03 Ally McBeal.mp3','Ally McBeal','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(5,1,'04 Starsky And Hutch.mp3','Starsky And Hutch','Tom Scott',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(6,1,'04 Will & Grace.mp3','Will & Grace','Various Artists',27639,2,44100,16,257,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(7,1,'05 A Question Of Sport.mp3','A Question Of Sport','Gordon Lorenz Orchestra',25183,2,44100,16,257,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(8,1,'06 Frasier.mp3','Frasier','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(9,1,'07 Friends.mp3','Friends','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(10,1,'07 Ski Sunday (Pop Looks Bach).mp3','Ski Sunday','Gordon Lorenz Orchestra',30016,2,44100,16,257,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(11,1,'08 Dangermouse.mp3','Dangermouse','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(12,1,'08 The Rockford Files.mp3','The Rockford Files','Mike Post & Pete Carpenter',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(13,1,'09 Doctor Who.mp3','Doctor Who','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(14,1,'10 The Six Million Dollar Man.mp3','The Six Million Dollar Man','Dusty Springfield',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(15,1,'11 M-A-S-H.mp3','M*A*S*H','Johnny Mandel',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(16,1,'12 The Waltons.mp3','The Waltons','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(17,1,'14 Black Beauty.mp3','Black Beauty','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(18,1,'14 The Simpsons.mp3','The Simpsons','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(19,1,'15 Home And Away.mp3','Home And Away','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(20,1,'15 thirtysomething.mp3','thirtysomething','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(21,1,'15 Thunderbirds.mp3','Thunderbirds','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(22,1,'16 Dogtanian.mp3','Dogtanian','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(23,1,'17 The Odd Couple.mp3','The Odd Couple','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(24,1,'18 Blockbusters.mp3','Blockbusters','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(25,1,'18 L.A. Law.mp3','L.A. Law','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(26,1,'18 Neighbours.mp3','Neighbours','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(27,1,'19 Happy Days.mp3','Happy Days','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(28,1,'19 Paddington Bear.mp3','Paddington Bear','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(29,1,'20 Pink Panther.mp3','Pink Panther','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(30,1,'20 Sesame Street.mp3','Sesame Street','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(31,1,'20 The X Files.mp3','The X Files','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(32,1,'21 Star Trek.mp3','Star Trek','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(33,1,'22 Moonlighting.mp3','Moonlighting','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(34,1,'22 Snooker (Drag Racer).mp3','Snooker','Gordon Lorenz Orchestra',30016,2,44100,16,257,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(35,1,'24 Blackadder.mp3','Blackadder','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(36,1,'24 Miami Vice.mp3','Miami Vice','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(37,1,'24 Scooby-Doo.mp3','Scooby-Doo','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(38,1,'25 Cricket (Soul Limbo).mp3','Cricket','Gordon Lorenz Orchestra',30016,2,44100,16,257,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(39,1,'25 Hawaii Five-0.mp3','Hawaii Five-0','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(40,1,'25 Monty Python''s Flying Circus (The Liberty Bell).mp3','Monty Python''s Flying Circus','Gordon Lorenz Orchestra',30016,2,44100,16,257,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(41,1,'26 The A-Team.mp3','The A-Team','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(42,1,'26 The Banana Splits.mp3','The Banana Splits','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(43,1,'27 Brookside.mp3','Brookside','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(44,1,'28 Cheers.mp3','Cheers','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(45,1,'28 Coronation Street.mp3','Coronation Street','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(46,1,'28 Grand Prix.mp3','Grand Prix','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(47,1,'29 Horse Of The Year.mp3','Horse Of The Year','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(48,1,'29 Knight Rider.mp3','Knight Rider','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(49,1,'29 The Monkees.mp3','The Monkees','The Monkees',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(50,1,'30 Batman.mp3','Batman','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(51,1,'30 Cagney & Lacey.mp3','Cagney & Lacey','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(52,1,'32 Hill Street Blues.mp3','Hill Street Blues','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(53,1,'33 Emmerdale.mp3','Emmerdale','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(54,1,'34 Magnum, P.I.mp3','Magnum, P.I.','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(55,1,'35 The Addams Family.mp3','The Addams Family','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(56,1,'36 Diff''rent Strokes.mp3','Diff''rent Strokes','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(57,1,'38 Bergerac.mp3','Bergerac','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(58,1,'38 Taxi.mp3','Taxi','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(59,1,'39 Dallas.mp3','Dallas','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(60,1,'40 The Flintstones.mp3','The Flintstones','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(61,1,'41 The Love Boat.mp3','The Love Boat','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(62,1,'45 Wonder Woman.mp3','Wonder Woman','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(63,1,'46 Charlie''s Angels.mp3','Charlie''s Angels','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(64,1,'46 Men Behaving Badly.mp3','Men Behaving Badly','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(65,1,'46 Steptoe And Son.mp3','Steptoe And Son','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(66,1,'47 Fawlty Towers.mp3','Fawlty Towers','Gordon Lorenz Orchestra',22989,2,44100,16,257,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(67,1,'47 Looney Tunes.mp3','Looney Tunes','Various Artists',11652,2,44100,16,257,'All-Time Top 100 TV Themes [Disc 2]');
INSERT INTO Song VALUES(68,1,'47 The Muppet Show.mp3','The Muppet Show','Various Artists',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]');
INSERT INTO Song VALUES(69,1,'48 The Sweeney.mp3','The Sweeney','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(70,1,'50 Porridge.mp3','Porridge','Gordon Lorenz Orchestra',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes');
INSERT INTO Song VALUES(71,1,'Wish You Were Here.mp3','Wish You Were Here (The Carnival)','Gordon Giltrap',30016,2,44100,16,257,'100 Hits  Guitar Heroes Disc 4');
CREATE TABLE IF NOT EXISTS "Track" (
  "pk" INTEGER PRIMARY KEY AUTOINCREMENT,
  "number" INTEGER UNSIGNED NOT NULL,
  "start_time" INTEGER UNSIGNED NOT NULL,
  "game" INTEGER NOT NULL REFERENCES "Game" ("pk") ON DELETE CASCADE,
  "song" INTEGER NOT NULL REFERENCES "Song" ("pk") ON DELETE CASCADE,
  CONSTRAINT "unq_track__number_game" UNIQUE ("number", "game")
);
INSERT INTO Track VALUES(6233,0,9048,5,49);
INSERT INTO Track VALUES(6234,1,39072,5,34);
INSERT INTO Track VALUES(6235,2,69096,5,7);
INSERT INTO Track VALUES(6236,3,94287,5,41);
INSERT INTO Track VALUES(6237,4,124311,5,28);
INSERT INTO Track VALUES(6238,5,154335,5,10);
INSERT INTO Track VALUES(6239,6,184359,5,2);
INSERT INTO Track VALUES(6240,7,214383,5,9);
INSERT INTO Track VALUES(6241,8,244407,5,63);
INSERT INTO Track VALUES(6242,9,274431,5,56);
INSERT INTO Track VALUES(6243,10,304455,5,59);
INSERT INTO Track VALUES(6244,11,334479,5,20);
INSERT INTO Track VALUES(6245,12,364503,5,60);
INSERT INTO Track VALUES(6246,13,394527,5,18);
INSERT INTO Track VALUES(6247,14,424551,5,71);
INSERT INTO Track VALUES(6248,15,454575,5,13);
INSERT INTO Track VALUES(6249,16,484599,5,33);
INSERT INTO Track VALUES(6250,17,514623,5,54);
INSERT INTO Track VALUES(6251,18,544647,5,21);
INSERT INTO Track VALUES(6252,19,574671,5,8);
INSERT INTO Track VALUES(6253,20,604695,5,55);
INSERT INTO Track VALUES(6254,21,634719,5,61);
INSERT INTO Track VALUES(6255,22,664743,5,14);
INSERT INTO Track VALUES(6256,23,694767,5,22);
INSERT INTO Track VALUES(6257,24,724791,5,62);
INSERT INTO Track VALUES(6258,25,754815,5,1);
INSERT INTO Track VALUES(6259,26,784839,5,66);
INSERT INTO Track VALUES(6260,27,807836,5,15);
INSERT INTO Track VALUES(6261,28,837860,5,23);
INSERT INTO Track VALUES(6262,29,867884,5,69);
INSERT INTO Track VALUES(6263,30,897908,5,32);
INSERT INTO Track VALUES(6264,31,927932,5,31);
INSERT INTO Track VALUES(6265,32,957956,5,38);
INSERT INTO Track VALUES(6266,33,987980,5,27);
INSERT INTO Track VALUES(6267,34,1018004,5,17);
INSERT INTO Track VALUES(6268,35,1048028,5,67);
INSERT INTO Track VALUES(6269,36,1059688,5,19);
INSERT INTO Track VALUES(6270,37,1089712,5,4);
INSERT INTO Track VALUES(6271,38,1119736,5,64);
INSERT INTO Track VALUES(6272,39,1149760,5,11);
INSERT INTO Track VALUES(6273,40,1179784,5,26);
INSERT INTO Track VALUES(6274,41,1209808,5,43);
INSERT INTO Track VALUES(6275,42,1239832,5,29);
INSERT INTO Track VALUES(6276,43,1269856,5,46);
INSERT INTO Track VALUES(6277,44,1299880,5,50);
INSERT INTO Track VALUES(6278,45,1329904,5,37);
INSERT INTO Track VALUES(6279,46,1359928,5,36);
INSERT INTO Track VALUES(6280,47,1389952,5,16);
INSERT INTO Track VALUES(6281,48,1419976,5,3);
INSERT INTO Track VALUES(6282,49,1450000,5,35);
CREATE TABLE IF NOT EXISTS "User" (
  "pk" INTEGER PRIMARY KEY AUTOINCREMENT,
  "username" VARCHAR(32) UNIQUE NOT NULL,
  "password" TEXT NOT NULL,
  "email" TEXT UNIQUE,
  "last_login" DATETIME,
  "groups_mask" INTEGER NOT NULL
);
INSERT INTO User VALUES(1,'admin','$2b$12$H8xhXO1D1t74YL2Ya2s6O.Kw7jGvWQjKci1y4E7L8ZAgrFE2EAanW','admin@music.bingo',NULL,1073741825);
CREATE TABLE IF NOT EXISTS "BingoTicket" (
  "pk" INTEGER PRIMARY KEY AUTOINCREMENT,
  "user" INTEGER REFERENCES "User" ("pk") ON DELETE SET NULL,
  "game" INTEGER NOT NULL REFERENCES "Game" ("pk") ON DELETE CASCADE,
  "number" INTEGER UNSIGNED NOT NULL,
  "fingerprint" TEXT NOT NULL,
  "order" JSON NOT NULL,
  "checked" BIGINT,
  CONSTRAINT "unq_bingoticket__game_number" UNIQUE ("game", "number")
);
INSERT INTO BingoTicket VALUES(97,NULL,5,1,'137842000276547756267607297119','[6259,6278,6256,6282,6252,6241,6242,6271,6274,6275,6260,6264,6244,6273,6238]',0);
INSERT INTO BingoTicket VALUES(98,NULL,5,9,'283954211299785196597543535','[6252,6242,6239,6279,6282,6240,6271,6255,6246,6262,6244,6254,6275,6247,6235]',0);
INSERT INTO BingoTicket VALUES(99,NULL,5,17,'3093561119661660795158752469521','[6252,6258,6238,6281,6271,6278,6260,6262,6265,6282,6245,6272,6246,6276,6277]',0);
INSERT INTO BingoTicket VALUES(100,NULL,5,2,'3976452437590616476533328505','[6272,6271,6274,6273,6235,6282,6252,6260,6246,6279,6247,6254,6236,6261,6240]',0);
INSERT INTO BingoTicket VALUES(101,NULL,5,10,'392517808361938290505320193983','[6263,6254,6242,6234,6273,6264,6276,6247,6266,6261,6279,6265,6260,6277,6282]',0);
INSERT INTO BingoTicket VALUES(102,NULL,5,18,'56083267314458093539386986','[6271,6238,6239,6280,6237,6260,6265,6274,6251,6255,6244,6264,6250,6233,6252]',0);
INSERT INTO BingoTicket VALUES(103,NULL,5,3,'578209721924019749968315923','[6249,6234,6255,6266,6237,6241,6246,6270,6277,6273,6268,6260,6247,6256,6251]',0);
INSERT INTO BingoTicket VALUES(104,NULL,5,11,'382407899075551600600660449409','[6242,6257,6269,6272,6263,6260,6273,6256,6281,6262,6239,6267,6244,6249,6270]',0);
INSERT INTO BingoTicket VALUES(105,NULL,5,19,'5743535842924635965947835083','[6242,6265,6276,6271,6274,6247,6268,6248,6253,6239,6243,6273,6254,6236,6272]',0);
INSERT INTO BingoTicket VALUES(106,NULL,5,4,'548689728794393997483166514285','[6255,6267,6256,6269,6281,6260,6254,6271,6272,6273,6251,6235,6282,6246,6257]',0);
INSERT INTO BingoTicket VALUES(107,NULL,5,12,'181532871627159486833217619957','[6257,6272,6271,6281,6256,6255,6246,6282,6238,6251,6267,6261,6264,6242,6253]',0);
INSERT INTO BingoTicket VALUES(108,NULL,5,20,'5682284329918661534183565','[6240,6247,6255,6259,6237,6280,6241,6264,6243,6271,6234,6277,6281,6242,6235]',0);
INSERT INTO BingoTicket VALUES(109,NULL,5,5,'3281899216632339278903953993','[6281,6268,6265,6273,6252,6240,6237,6254,6263,6246,6239,6275,6255,6253,6243]',0);
INSERT INTO BingoTicket VALUES(110,NULL,5,13,'64696482373920204551500973935','[6274,6249,6260,6279,6250,6251,6246,6244,6263,6271,6235,6268,6264,6275,6259]',0);
INSERT INTO BingoTicket VALUES(111,NULL,5,21,'4737641249456067650221359914','[6269,6249,6238,6255,6278,6282,6271,6268,6233,6257,6254,6262,6246,6275,6242]',0);
INSERT INTO BingoTicket VALUES(112,NULL,5,6,'128083589153059696336631770','[6257,6264,6267,6241,6239,6247,6278,6282,6235,6280,6281,6237,6270,6233,6256]',0);
INSERT INTO BingoTicket VALUES(113,NULL,5,14,'5140345345837677997220184359','[6242,6263,6250,6272,6248,6282,6239,6271,6270,6264,6252,6237,6247,6255,6249]',0);
INSERT INTO BingoTicket VALUES(114,NULL,5,22,'894196174524236874124536163','[6245,6259,6240,6282,6239,6273,6243,6257,6266,6237,6236,6253,6281,6275,6269]',0);
INSERT INTO BingoTicket VALUES(115,NULL,5,7,'228493148981335956743925382','[6233,6278,6245,6259,6252,6269,6270,6257,6275,6241,6236,6246,6250,6253,6264]',0);
INSERT INTO BingoTicket VALUES(116,NULL,5,15,'512905498954167636910315247599','[6271,6259,6242,6239,6249,6278,6243,6262,6252,6265,6272,6261,6280,6269,6282]',0);
INSERT INTO BingoTicket VALUES(117,NULL,5,23,'565347632972216757686486426759','[6255,6248,6254,6282,6244,6262,6276,6266,6258,6251,6277,6249,6269,6241,6280]',0);
INSERT INTO BingoTicket VALUES(118,NULL,5,8,'3749066119782370711926027478','[6242,6275,6273,6258,6243,6267,6233,6260,6274,6281,6251,6268,6238,6246,6270]',0);
INSERT INTO BingoTicket VALUES(119,NULL,5,16,'1490162226947038795387715094','[6234,6260,6252,6276,6272,6256,6275,6246,6257,6261,6254,6247,6282,6267,6233]',0);
INSERT INTO BingoTicket VALUES(120,NULL,5,24,'1260859006682829152811909741263','[6250,6256,6254,6263,6259,6264,6239,6267,6266,6281,6274,6272,6275,6244,6257]',0);
CREATE TABLE IF NOT EXISTS "BingoTicket_Track" (
  "bingoticket" INTEGER NOT NULL REFERENCES "BingoTicket" ("pk") ON DELETE CASCADE,
  "track" INTEGER NOT NULL REFERENCES "Track" ("pk") ON DELETE CASCADE,
  PRIMARY KEY ("bingoticket", "track")
);
INSERT INTO BingoTicket_Track VALUES(97,6256);
INSERT INTO BingoTicket_Track VALUES(97,6260);
INSERT INTO BingoTicket_Track VALUES(97,6264);
INSERT INTO BingoTicket_Track VALUES(97,6273);
INSERT INTO BingoTicket_Track VALUES(97,6252);
INSERT INTO BingoTicket_Track VALUES(97,6271);
INSERT INTO BingoTicket_Track VALUES(97,6242);
INSERT INTO BingoTicket_Track VALUES(97,6274);
INSERT INTO BingoTicket_Track VALUES(97,6275);
INSERT INTO BingoTicket_Track VALUES(97,6244);
INSERT INTO BingoTicket_Track VALUES(97,6238);
INSERT INTO BingoTicket_Track VALUES(97,6241);
INSERT INTO BingoTicket_Track VALUES(97,6259);
INSERT INTO BingoTicket_Track VALUES(97,6278);
INSERT INTO BingoTicket_Track VALUES(97,6282);
INSERT INTO BingoTicket_Track VALUES(98,6262);
INSERT INTO BingoTicket_Track VALUES(98,6254);
INSERT INTO BingoTicket_Track VALUES(98,6279);
INSERT INTO BingoTicket_Track VALUES(98,6242);
INSERT INTO BingoTicket_Track VALUES(98,6252);
INSERT INTO BingoTicket_Track VALUES(98,6240);
INSERT INTO BingoTicket_Track VALUES(98,6271);
INSERT INTO BingoTicket_Track VALUES(98,6246);
INSERT INTO BingoTicket_Track VALUES(98,6244);
INSERT INTO BingoTicket_Track VALUES(98,6275);
INSERT INTO BingoTicket_Track VALUES(98,6235);
INSERT INTO BingoTicket_Track VALUES(98,6255);
INSERT INTO BingoTicket_Track VALUES(98,6247);
INSERT INTO BingoTicket_Track VALUES(98,6239);
INSERT INTO BingoTicket_Track VALUES(98,6282);
INSERT INTO BingoTicket_Track VALUES(99,6276);
INSERT INTO BingoTicket_Track VALUES(99,6282);
INSERT INTO BingoTicket_Track VALUES(99,6245);
INSERT INTO BingoTicket_Track VALUES(99,6278);
INSERT INTO BingoTicket_Track VALUES(99,6272);
INSERT INTO BingoTicket_Track VALUES(99,6265);
INSERT INTO BingoTicket_Track VALUES(99,6252);
INSERT INTO BingoTicket_Track VALUES(99,6281);
INSERT INTO BingoTicket_Track VALUES(99,6238);
INSERT INTO BingoTicket_Track VALUES(99,6271);
INSERT INTO BingoTicket_Track VALUES(99,6246);
INSERT INTO BingoTicket_Track VALUES(99,6277);
INSERT INTO BingoTicket_Track VALUES(99,6260);
INSERT INTO BingoTicket_Track VALUES(99,6262);
INSERT INTO BingoTicket_Track VALUES(99,6258);
INSERT INTO BingoTicket_Track VALUES(100,6246);
INSERT INTO BingoTicket_Track VALUES(100,6261);
INSERT INTO BingoTicket_Track VALUES(100,6235);
INSERT INTO BingoTicket_Track VALUES(100,6236);
INSERT INTO BingoTicket_Track VALUES(100,6252);
INSERT INTO BingoTicket_Track VALUES(100,6279);
INSERT INTO BingoTicket_Track VALUES(100,6247);
INSERT INTO BingoTicket_Track VALUES(100,6282);
INSERT INTO BingoTicket_Track VALUES(100,6240);
INSERT INTO BingoTicket_Track VALUES(100,6272);
INSERT INTO BingoTicket_Track VALUES(100,6273);
INSERT INTO BingoTicket_Track VALUES(100,6260);
INSERT INTO BingoTicket_Track VALUES(100,6254);
INSERT INTO BingoTicket_Track VALUES(100,6271);
INSERT INTO BingoTicket_Track VALUES(100,6274);
INSERT INTO BingoTicket_Track VALUES(101,6242);
INSERT INTO BingoTicket_Track VALUES(101,6263);
INSERT INTO BingoTicket_Track VALUES(101,6279);
INSERT INTO BingoTicket_Track VALUES(101,6277);
INSERT INTO BingoTicket_Track VALUES(101,6261);
INSERT INTO BingoTicket_Track VALUES(101,6273);
INSERT INTO BingoTicket_Track VALUES(101,6234);
INSERT INTO BingoTicket_Track VALUES(101,6254);
INSERT INTO BingoTicket_Track VALUES(101,6264);
INSERT INTO BingoTicket_Track VALUES(101,6266);
INSERT INTO BingoTicket_Track VALUES(101,6260);
INSERT INTO BingoTicket_Track VALUES(101,6282);
INSERT INTO BingoTicket_Track VALUES(101,6247);
INSERT INTO BingoTicket_Track VALUES(101,6276);
INSERT INTO BingoTicket_Track VALUES(101,6265);
INSERT INTO BingoTicket_Track VALUES(102,6260);
INSERT INTO BingoTicket_Track VALUES(102,6239);
INSERT INTO BingoTicket_Track VALUES(102,6264);
INSERT INTO BingoTicket_Track VALUES(102,6280);
INSERT INTO BingoTicket_Track VALUES(102,6237);
INSERT INTO BingoTicket_Track VALUES(102,6238);
INSERT INTO BingoTicket_Track VALUES(102,6271);
INSERT INTO BingoTicket_Track VALUES(102,6274);
INSERT INTO BingoTicket_Track VALUES(102,6244);
INSERT INTO BingoTicket_Track VALUES(102,6250);
INSERT INTO BingoTicket_Track VALUES(102,6252);
INSERT INTO BingoTicket_Track VALUES(102,6251);
INSERT INTO BingoTicket_Track VALUES(102,6265);
INSERT INTO BingoTicket_Track VALUES(102,6255);
INSERT INTO BingoTicket_Track VALUES(102,6233);
INSERT INTO BingoTicket_Track VALUES(103,6273);
INSERT INTO BingoTicket_Track VALUES(103,6241);
INSERT INTO BingoTicket_Track VALUES(103,6247);
INSERT INTO BingoTicket_Track VALUES(103,6256);
INSERT INTO BingoTicket_Track VALUES(103,6251);
INSERT INTO BingoTicket_Track VALUES(103,6249);
INSERT INTO BingoTicket_Track VALUES(103,6270);
INSERT INTO BingoTicket_Track VALUES(103,6255);
INSERT INTO BingoTicket_Track VALUES(103,6260);
INSERT INTO BingoTicket_Track VALUES(103,6277);
INSERT INTO BingoTicket_Track VALUES(103,6237);
INSERT INTO BingoTicket_Track VALUES(103,6246);
INSERT INTO BingoTicket_Track VALUES(103,6268);
INSERT INTO BingoTicket_Track VALUES(103,6266);
INSERT INTO BingoTicket_Track VALUES(103,6234);
INSERT INTO BingoTicket_Track VALUES(104,6242);
INSERT INTO BingoTicket_Track VALUES(104,6267);
INSERT INTO BingoTicket_Track VALUES(104,6257);
INSERT INTO BingoTicket_Track VALUES(104,6263);
INSERT INTO BingoTicket_Track VALUES(104,6244);
INSERT INTO BingoTicket_Track VALUES(104,6249);
INSERT INTO BingoTicket_Track VALUES(104,6239);
INSERT INTO BingoTicket_Track VALUES(104,6270);
INSERT INTO BingoTicket_Track VALUES(104,6272);
INSERT INTO BingoTicket_Track VALUES(104,6260);
INSERT INTO BingoTicket_Track VALUES(104,6273);
INSERT INTO BingoTicket_Track VALUES(104,6281);
INSERT INTO BingoTicket_Track VALUES(104,6256);
INSERT INTO BingoTicket_Track VALUES(104,6262);
INSERT INTO BingoTicket_Track VALUES(104,6269);
INSERT INTO BingoTicket_Track VALUES(105,6242);
INSERT INTO BingoTicket_Track VALUES(105,6274);
INSERT INTO BingoTicket_Track VALUES(105,6271);
INSERT INTO BingoTicket_Track VALUES(105,6268);
INSERT INTO BingoTicket_Track VALUES(105,6248);
INSERT INTO BingoTicket_Track VALUES(105,6265);
INSERT INTO BingoTicket_Track VALUES(105,6273);
INSERT INTO BingoTicket_Track VALUES(105,6254);
INSERT INTO BingoTicket_Track VALUES(105,6272);
INSERT INTO BingoTicket_Track VALUES(105,6253);
INSERT INTO BingoTicket_Track VALUES(105,6239);
INSERT INTO BingoTicket_Track VALUES(105,6243);
INSERT INTO BingoTicket_Track VALUES(105,6247);
INSERT INTO BingoTicket_Track VALUES(105,6276);
INSERT INTO BingoTicket_Track VALUES(105,6236);
INSERT INTO BingoTicket_Track VALUES(106,6256);
INSERT INTO BingoTicket_Track VALUES(106,6260);
INSERT INTO BingoTicket_Track VALUES(106,6254);
INSERT INTO BingoTicket_Track VALUES(106,6272);
INSERT INTO BingoTicket_Track VALUES(106,6273);
INSERT INTO BingoTicket_Track VALUES(106,6251);
INSERT INTO BingoTicket_Track VALUES(106,6281);
INSERT INTO BingoTicket_Track VALUES(106,6269);
INSERT INTO BingoTicket_Track VALUES(106,6271);
INSERT INTO BingoTicket_Track VALUES(106,6246);
INSERT INTO BingoTicket_Track VALUES(106,6267);
INSERT INTO BingoTicket_Track VALUES(106,6255);
INSERT INTO BingoTicket_Track VALUES(106,6257);
INSERT INTO BingoTicket_Track VALUES(106,6235);
INSERT INTO BingoTicket_Track VALUES(106,6282);
INSERT INTO BingoTicket_Track VALUES(107,6251);
INSERT INTO BingoTicket_Track VALUES(107,6282);
INSERT INTO BingoTicket_Track VALUES(107,6256);
INSERT INTO BingoTicket_Track VALUES(107,6261);
INSERT INTO BingoTicket_Track VALUES(107,6255);
INSERT INTO BingoTicket_Track VALUES(107,6257);
INSERT INTO BingoTicket_Track VALUES(107,6267);
INSERT INTO BingoTicket_Track VALUES(107,6253);
INSERT INTO BingoTicket_Track VALUES(107,6281);
INSERT INTO BingoTicket_Track VALUES(107,6271);
INSERT INTO BingoTicket_Track VALUES(107,6246);
INSERT INTO BingoTicket_Track VALUES(107,6238);
INSERT INTO BingoTicket_Track VALUES(107,6242);
INSERT INTO BingoTicket_Track VALUES(107,6264);
INSERT INTO BingoTicket_Track VALUES(107,6272);
INSERT INTO BingoTicket_Track VALUES(108,6234);
INSERT INTO BingoTicket_Track VALUES(108,6280);
INSERT INTO BingoTicket_Track VALUES(108,6241);
INSERT INTO BingoTicket_Track VALUES(108,6243);
INSERT INTO BingoTicket_Track VALUES(108,6247);
INSERT INTO BingoTicket_Track VALUES(108,6255);
INSERT INTO BingoTicket_Track VALUES(108,6259);
INSERT INTO BingoTicket_Track VALUES(108,6235);
INSERT INTO BingoTicket_Track VALUES(108,6237);
INSERT INTO BingoTicket_Track VALUES(108,6240);
INSERT INTO BingoTicket_Track VALUES(108,6271);
INSERT INTO BingoTicket_Track VALUES(108,6277);
INSERT INTO BingoTicket_Track VALUES(108,6281);
INSERT INTO BingoTicket_Track VALUES(108,6242);
INSERT INTO BingoTicket_Track VALUES(108,6264);
INSERT INTO BingoTicket_Track VALUES(109,6265);
INSERT INTO BingoTicket_Track VALUES(109,6253);
INSERT INTO BingoTicket_Track VALUES(109,6255);
INSERT INTO BingoTicket_Track VALUES(109,6263);
INSERT INTO BingoTicket_Track VALUES(109,6240);
INSERT INTO BingoTicket_Track VALUES(109,6275);
INSERT INTO BingoTicket_Track VALUES(109,6237);
INSERT INTO BingoTicket_Track VALUES(109,6243);
INSERT INTO BingoTicket_Track VALUES(109,6239);
INSERT INTO BingoTicket_Track VALUES(109,6273);
INSERT INTO BingoTicket_Track VALUES(109,6268);
INSERT INTO BingoTicket_Track VALUES(109,6254);
INSERT INTO BingoTicket_Track VALUES(109,6246);
INSERT INTO BingoTicket_Track VALUES(109,6281);
INSERT INTO BingoTicket_Track VALUES(109,6252);
INSERT INTO BingoTicket_Track VALUES(110,6274);
INSERT INTO BingoTicket_Track VALUES(110,6235);
INSERT INTO BingoTicket_Track VALUES(110,6250);
INSERT INTO BingoTicket_Track VALUES(110,6279);
INSERT INTO BingoTicket_Track VALUES(110,6246);
INSERT INTO BingoTicket_Track VALUES(110,6244);
INSERT INTO BingoTicket_Track VALUES(110,6263);
INSERT INTO BingoTicket_Track VALUES(110,6271);
INSERT INTO BingoTicket_Track VALUES(110,6268);
INSERT INTO BingoTicket_Track VALUES(110,6275);
INSERT INTO BingoTicket_Track VALUES(110,6260);
INSERT INTO BingoTicket_Track VALUES(110,6264);
INSERT INTO BingoTicket_Track VALUES(110,6251);
INSERT INTO BingoTicket_Track VALUES(110,6249);
INSERT INTO BingoTicket_Track VALUES(110,6259);
INSERT INTO BingoTicket_Track VALUES(111,6254);
INSERT INTO BingoTicket_Track VALUES(111,6262);
INSERT INTO BingoTicket_Track VALUES(111,6278);
INSERT INTO BingoTicket_Track VALUES(111,6269);
INSERT INTO BingoTicket_Track VALUES(111,6238);
INSERT INTO BingoTicket_Track VALUES(111,6271);
INSERT INTO BingoTicket_Track VALUES(111,6268);
INSERT INTO BingoTicket_Track VALUES(111,6246);
INSERT INTO BingoTicket_Track VALUES(111,6275);
INSERT INTO BingoTicket_Track VALUES(111,6242);
INSERT INTO BingoTicket_Track VALUES(111,6249);
INSERT INTO BingoTicket_Track VALUES(111,6257);
INSERT INTO BingoTicket_Track VALUES(111,6255);
INSERT INTO BingoTicket_Track VALUES(111,6233);
INSERT INTO BingoTicket_Track VALUES(111,6282);
INSERT INTO BingoTicket_Track VALUES(112,6270);
INSERT INTO BingoTicket_Track VALUES(112,6282);
INSERT INTO BingoTicket_Track VALUES(112,6280);
INSERT INTO BingoTicket_Track VALUES(112,6278);
INSERT INTO BingoTicket_Track VALUES(112,6233);
INSERT INTO BingoTicket_Track VALUES(112,6256);
INSERT INTO BingoTicket_Track VALUES(112,6241);
INSERT INTO BingoTicket_Track VALUES(112,6247);
INSERT INTO BingoTicket_Track VALUES(112,6239);
INSERT INTO BingoTicket_Track VALUES(112,6257);
INSERT INTO BingoTicket_Track VALUES(112,6267);
INSERT INTO BingoTicket_Track VALUES(112,6235);
INSERT INTO BingoTicket_Track VALUES(112,6281);
INSERT INTO BingoTicket_Track VALUES(112,6237);
INSERT INTO BingoTicket_Track VALUES(112,6264);
INSERT INTO BingoTicket_Track VALUES(113,6263);
INSERT INTO BingoTicket_Track VALUES(113,6255);
INSERT INTO BingoTicket_Track VALUES(113,6271);
INSERT INTO BingoTicket_Track VALUES(113,6237);
INSERT INTO BingoTicket_Track VALUES(113,6242);
INSERT INTO BingoTicket_Track VALUES(113,6239);
INSERT INTO BingoTicket_Track VALUES(113,6247);
INSERT INTO BingoTicket_Track VALUES(113,6249);
INSERT INTO BingoTicket_Track VALUES(113,6282);
INSERT INTO BingoTicket_Track VALUES(113,6270);
INSERT INTO BingoTicket_Track VALUES(113,6272);
INSERT INTO BingoTicket_Track VALUES(113,6264);
INSERT INTO BingoTicket_Track VALUES(113,6252);
INSERT INTO BingoTicket_Track VALUES(113,6248);
INSERT INTO BingoTicket_Track VALUES(113,6250);
INSERT INTO BingoTicket_Track VALUES(114,6240);
INSERT INTO BingoTicket_Track VALUES(114,6237);
INSERT INTO BingoTicket_Track VALUES(114,6281);
INSERT INTO BingoTicket_Track VALUES(114,6275);
INSERT INTO BingoTicket_Track VALUES(114,6269);
INSERT INTO BingoTicket_Track VALUES(114,6273);
INSERT INTO BingoTicket_Track VALUES(114,6266);
INSERT INTO BingoTicket_Track VALUES(114,6253);
INSERT INTO BingoTicket_Track VALUES(114,6257);
INSERT INTO BingoTicket_Track VALUES(114,6236);
INSERT INTO BingoTicket_Track VALUES(114,6239);
INSERT INTO BingoTicket_Track VALUES(114,6243);
INSERT INTO BingoTicket_Track VALUES(114,6245);
INSERT INTO BingoTicket_Track VALUES(114,6282);
INSERT INTO BingoTicket_Track VALUES(114,6259);
INSERT INTO BingoTicket_Track VALUES(115,6264);
INSERT INTO BingoTicket_Track VALUES(115,6252);
INSERT INTO BingoTicket_Track VALUES(115,6269);
INSERT INTO BingoTicket_Track VALUES(115,6275);
INSERT INTO BingoTicket_Track VALUES(115,6246);
INSERT INTO BingoTicket_Track VALUES(115,6250);
INSERT INTO BingoTicket_Track VALUES(115,6270);
INSERT INTO BingoTicket_Track VALUES(115,6236);
INSERT INTO BingoTicket_Track VALUES(115,6257);
INSERT INTO BingoTicket_Track VALUES(115,6253);
INSERT INTO BingoTicket_Track VALUES(115,6259);
INSERT INTO BingoTicket_Track VALUES(115,6233);
INSERT INTO BingoTicket_Track VALUES(115,6241);
INSERT INTO BingoTicket_Track VALUES(115,6278);
INSERT INTO BingoTicket_Track VALUES(115,6245);
INSERT INTO BingoTicket_Track VALUES(116,6280);
INSERT INTO BingoTicket_Track VALUES(116,6278);
INSERT INTO BingoTicket_Track VALUES(116,6282);
INSERT INTO BingoTicket_Track VALUES(116,6239);
INSERT INTO BingoTicket_Track VALUES(116,6272);
INSERT INTO BingoTicket_Track VALUES(116,6243);
INSERT INTO BingoTicket_Track VALUES(116,6249);
INSERT INTO BingoTicket_Track VALUES(116,6259);
INSERT INTO BingoTicket_Track VALUES(116,6265);
INSERT INTO BingoTicket_Track VALUES(116,6261);
INSERT INTO BingoTicket_Track VALUES(116,6271);
INSERT INTO BingoTicket_Track VALUES(116,6242);
INSERT INTO BingoTicket_Track VALUES(116,6252);
INSERT INTO BingoTicket_Track VALUES(116,6269);
INSERT INTO BingoTicket_Track VALUES(116,6262);
INSERT INTO BingoTicket_Track VALUES(117,6255);
INSERT INTO BingoTicket_Track VALUES(117,6277);
INSERT INTO BingoTicket_Track VALUES(117,6280);
INSERT INTO BingoTicket_Track VALUES(117,6276);
INSERT INTO BingoTicket_Track VALUES(117,6241);
INSERT INTO BingoTicket_Track VALUES(117,6244);
INSERT INTO BingoTicket_Track VALUES(117,6249);
INSERT INTO BingoTicket_Track VALUES(117,6251);
INSERT INTO BingoTicket_Track VALUES(117,6282);
INSERT INTO BingoTicket_Track VALUES(117,6254);
INSERT INTO BingoTicket_Track VALUES(117,6262);
INSERT INTO BingoTicket_Track VALUES(117,6266);
INSERT INTO BingoTicket_Track VALUES(117,6258);
INSERT INTO BingoTicket_Track VALUES(117,6269);
INSERT INTO BingoTicket_Track VALUES(117,6248);
INSERT INTO BingoTicket_Track VALUES(118,6242);
INSERT INTO BingoTicket_Track VALUES(118,6275);
INSERT INTO BingoTicket_Track VALUES(118,6274);
INSERT INTO BingoTicket_Track VALUES(118,6281);
INSERT INTO BingoTicket_Track VALUES(118,6268);
INSERT INTO BingoTicket_Track VALUES(118,6238);
INSERT INTO BingoTicket_Track VALUES(118,6246);
INSERT INTO BingoTicket_Track VALUES(118,6258);
INSERT INTO BingoTicket_Track VALUES(118,6273);
INSERT INTO BingoTicket_Track VALUES(118,6260);
INSERT INTO BingoTicket_Track VALUES(118,6233);
INSERT INTO BingoTicket_Track VALUES(118,6251);
INSERT INTO BingoTicket_Track VALUES(118,6243);
INSERT INTO BingoTicket_Track VALUES(118,6270);
INSERT INTO BingoTicket_Track VALUES(118,6267);
INSERT INTO BingoTicket_Track VALUES(119,6252);
INSERT INTO BingoTicket_Track VALUES(119,6275);
INSERT INTO BingoTicket_Track VALUES(119,6246);
INSERT INTO BingoTicket_Track VALUES(119,6257);
INSERT INTO BingoTicket_Track VALUES(119,6260);
INSERT INTO BingoTicket_Track VALUES(119,6234);
INSERT INTO BingoTicket_Track VALUES(119,6272);
INSERT INTO BingoTicket_Track VALUES(119,6256);
INSERT INTO BingoTicket_Track VALUES(119,6254);
INSERT INTO BingoTicket_Track VALUES(119,6282);
INSERT INTO BingoTicket_Track VALUES(119,6233);
INSERT INTO BingoTicket_Track VALUES(119,6261);
INSERT INTO BingoTicket_Track VALUES(119,6247);
INSERT INTO BingoTicket_Track VALUES(119,6276);
INSERT INTO BingoTicket_Track VALUES(119,6267);
INSERT INTO BingoTicket_Track VALUES(120,6254);
INSERT INTO BingoTicket_Track VALUES(120,6256);
INSERT INTO BingoTicket_Track VALUES(120,6264);
INSERT INTO BingoTicket_Track VALUES(120,6266);
INSERT INTO BingoTicket_Track VALUES(120,6272);
INSERT INTO BingoTicket_Track VALUES(120,6250);
INSERT INTO BingoTicket_Track VALUES(120,6281);
INSERT INTO BingoTicket_Track VALUES(120,6274);
INSERT INTO BingoTicket_Track VALUES(120,6275);
INSERT INTO BingoTicket_Track VALUES(120,6244);
INSERT INTO BingoTicket_Track VALUES(120,6259);
INSERT INTO BingoTicket_Track VALUES(120,6267);
INSERT INTO BingoTicket_Track VALUES(120,6257);
INSERT INTO BingoTicket_Track VALUES(120,6263);
INSERT INTO BingoTicket_Track VALUES(120,6239);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('User',1);
INSERT INTO sqlite_sequence VALUES('Directory',1);
INSERT INTO sqlite_sequence VALUES('Song',71);
INSERT INTO sqlite_sequence VALUES('Game',5);
INSERT INTO sqlite_sequence VALUES('Track',6282);
INSERT INTO sqlite_sequence VALUES('BingoTicket',120);
CREATE INDEX "idx_directory__directory" ON "Directory" ("directory");
CREATE INDEX "idx_song__filename" ON "Song" ("filename");
CREATE INDEX "idx_song__title" ON "Song" ("title");
CREATE INDEX "idx_track__game" ON "Track" ("game");
CREATE INDEX "idx_track__song" ON "Track" ("song");
CREATE INDEX "idx_bingoticket__user" ON "BingoTicket" ("user");
CREATE INDEX "idx_bingoticket_track" ON "BingoTicket_Track" ("track");
COMMIT;
