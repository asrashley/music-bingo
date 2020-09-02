PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "User" (
    pk INTEGER NOT NULL,
    username VARCHAR(32) NOT NULL,
    password VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    last_login DATETIME,
    groups_mask INTEGER NOT NULL,
    reset_date DATETIME,
    reset_token VARCHAR(32),
    PRIMARY KEY (pk),
    UNIQUE (username),
    UNIQUE (email)
);
INSERT INTO User VALUES(1,'admin','$2b$12$H8xhXO1D1t74YL2Ya2s6O.Kw7jGvWQjKci1y4E7L8ZAgrFE2EAanW','admin@music.bingo',NULL,1073741825,NULL,NULL);
CREATE TABLE IF NOT EXISTS "Game" (
    pk INTEGER NOT NULL,
    id VARCHAR(64) NOT NULL,
    title VARCHAR NOT NULL,
    start DATETIME NOT NULL,
    "end" DATETIME NOT NULL,
    options JSON,
    PRIMARY KEY (pk),
    UNIQUE (id),
    UNIQUE (start)
);
INSERT INTO Game VALUES(1,'20-04-24-2','TV Themes','2020-04-24 18:05:44.048300','2020-08-02 18:05:44.048300','null');
CREATE TABLE IF NOT EXISTS "Directory" (
    pk INTEGER NOT NULL,
    name VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    artist VARCHAR,
    directory INTEGER,
    PRIMARY KEY (pk),
    FOREIGN KEY(directory) REFERENCES "Directory" (pk)
);
INSERT INTO Directory VALUES(1,'Clips/TV Themes','[TV Themes]','',NULL);
CREATE TABLE IF NOT EXISTS "SchemaVersion" (
    "table" VARCHAR(32) NOT NULL,
    version INTEGER NOT NULL,
    PRIMARY KEY ("table")
);
INSERT INTO SchemaVersion VALUES('User',3);
INSERT INTO SchemaVersion VALUES('Directory',2);
INSERT INTO SchemaVersion VALUES('Song',2);
INSERT INTO SchemaVersion VALUES('Game',3);
INSERT INTO SchemaVersion VALUES('Track',2);
INSERT INTO SchemaVersion VALUES('BingoTicket',2);
CREATE TABLE IF NOT EXISTS "Song" (
    pk INTEGER NOT NULL,
    directory INTEGER NOT NULL,
    filename VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    artist VARCHAR,
    duration INTEGER NOT NULL,
    channels INTEGER NOT NULL,
    sample_rate INTEGER NOT NULL,
    sample_width INTEGER NOT NULL,
    bitrate INTEGER NOT NULL,
    album VARCHAR,
    PRIMARY KEY (pk),
    UNIQUE (directory, filename),
    FOREIGN KEY(directory) REFERENCES "Directory" (pk)
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
CREATE TABLE IF NOT EXISTS "BingoTicket" (
    pk INTEGER NOT NULL,
    user INTEGER,
    game INTEGER NOT NULL,
    number INTEGER NOT NULL,
    fingerprint VARCHAR NOT NULL,
    "order" JSON NOT NULL,
    checked BIGINT NOT NULL,
    PRIMARY KEY (pk),
    UNIQUE (game, number),
    FOREIGN KEY(user) REFERENCES "User" (pk),
    FOREIGN KEY(game) REFERENCES "Game" (pk)
);
INSERT INTO BingoTicket VALUES(1,NULL,1,1,'137842000276547756267607297119','[6259, 6278, 6256, 6282, 6252, 6241, 6242, 6271, 6274, 6275, 6260, 6264, 6244, 6273, 6238]',0);
INSERT INTO BingoTicket VALUES(2,NULL,1,9,'283954211299785196597543535','[6252, 6242, 6239, 6279, 6282, 6240, 6271, 6255, 6246, 6262, 6244, 6254, 6275, 6247, 6235]',0);
INSERT INTO BingoTicket VALUES(3,NULL,1,17,'3093561119661660795158752469521','[6252, 6258, 6238, 6281, 6271, 6278, 6260, 6262, 6265, 6282, 6245, 6272, 6246, 6276, 6277]',0);
INSERT INTO BingoTicket VALUES(4,NULL,1,2,'3976452437590616476533328505','[6272, 6271, 6274, 6273, 6235, 6282, 6252, 6260, 6246, 6279, 6247, 6254, 6236, 6261, 6240]',0);
INSERT INTO BingoTicket VALUES(5,NULL,1,10,'392517808361938290505320193983','[6263, 6254, 6242, 6234, 6273, 6264, 6276, 6247, 6266, 6261, 6279, 6265, 6260, 6277, 6282]',0);
INSERT INTO BingoTicket VALUES(6,NULL,1,18,'56083267314458093539386986','[6271, 6238, 6239, 6280, 6237, 6260, 6265, 6274, 6251, 6255, 6244, 6264, 6250, 6233, 6252]',0);
INSERT INTO BingoTicket VALUES(7,NULL,1,3,'578209721924019749968315923','[6249, 6234, 6255, 6266, 6237, 6241, 6246, 6270, 6277, 6273, 6268, 6260, 6247, 6256, 6251]',0);
INSERT INTO BingoTicket VALUES(8,NULL,1,11,'382407899075551600600660449409','[6242, 6257, 6269, 6272, 6263, 6260, 6273, 6256, 6281, 6262, 6239, 6267, 6244, 6249, 6270]',0);
INSERT INTO BingoTicket VALUES(9,NULL,1,19,'5743535842924635965947835083','[6242, 6265, 6276, 6271, 6274, 6247, 6268, 6248, 6253, 6239, 6243, 6273, 6254, 6236, 6272]',0);
INSERT INTO BingoTicket VALUES(10,NULL,1,4,'548689728794393997483166514285','[6255, 6267, 6256, 6269, 6281, 6260, 6254, 6271, 6272, 6273, 6251, 6235, 6282, 6246, 6257]',0);
INSERT INTO BingoTicket VALUES(11,NULL,1,12,'181532871627159486833217619957','[6257, 6272, 6271, 6281, 6256, 6255, 6246, 6282, 6238, 6251, 6267, 6261, 6264, 6242, 6253]',0);
INSERT INTO BingoTicket VALUES(12,NULL,1,20,'5682284329918661534183565','[6240, 6247, 6255, 6259, 6237, 6280, 6241, 6264, 6243, 6271, 6234, 6277, 6281, 6242, 6235]',0);
INSERT INTO BingoTicket VALUES(13,NULL,1,5,'3281899216632339278903953993','[6281, 6268, 6265, 6273, 6252, 6240, 6237, 6254, 6263, 6246, 6239, 6275, 6255, 6253, 6243]',0);
INSERT INTO BingoTicket VALUES(14,NULL,1,13,'64696482373920204551500973935','[6274, 6249, 6260, 6279, 6250, 6251, 6246, 6244, 6263, 6271, 6235, 6268, 6264, 6275, 6259]',0);
INSERT INTO BingoTicket VALUES(15,NULL,1,21,'4737641249456067650221359914','[6269, 6249, 6238, 6255, 6278, 6282, 6271, 6268, 6233, 6257, 6254, 6262, 6246, 6275, 6242]',0);
INSERT INTO BingoTicket VALUES(16,NULL,1,6,'128083589153059696336631770','[6257, 6264, 6267, 6241, 6239, 6247, 6278, 6282, 6235, 6280, 6281, 6237, 6270, 6233, 6256]',0);
INSERT INTO BingoTicket VALUES(17,NULL,1,14,'5140345345837677997220184359','[6242, 6263, 6250, 6272, 6248, 6282, 6239, 6271, 6270, 6264, 6252, 6237, 6247, 6255, 6249]',0);
INSERT INTO BingoTicket VALUES(18,NULL,1,22,'894196174524236874124536163','[6245, 6259, 6240, 6282, 6239, 6273, 6243, 6257, 6266, 6237, 6236, 6253, 6281, 6275, 6269]',0);
INSERT INTO BingoTicket VALUES(19,NULL,1,7,'228493148981335956743925382','[6233, 6278, 6245, 6259, 6252, 6269, 6270, 6257, 6275, 6241, 6236, 6246, 6250, 6253, 6264]',0);
INSERT INTO BingoTicket VALUES(20,NULL,1,15,'512905498954167636910315247599','[6271, 6259, 6242, 6239, 6249, 6278, 6243, 6262, 6252, 6265, 6272, 6261, 6280, 6269, 6282]',0);
INSERT INTO BingoTicket VALUES(21,NULL,1,23,'565347632972216757686486426759','[6255, 6248, 6254, 6282, 6244, 6262, 6276, 6266, 6258, 6251, 6277, 6249, 6269, 6241, 6280]',0);
INSERT INTO BingoTicket VALUES(22,NULL,1,8,'3749066119782370711926027478','[6242, 6275, 6273, 6258, 6243, 6267, 6233, 6260, 6274, 6281, 6251, 6268, 6238, 6246, 6270]',0);
INSERT INTO BingoTicket VALUES(23,NULL,1,16,'1490162226947038795387715094','[6234, 6260, 6252, 6276, 6272, 6256, 6275, 6246, 6257, 6261, 6254, 6247, 6282, 6267, 6233]',0);
INSERT INTO BingoTicket VALUES(24,NULL,1,24,'1260859006682829152811909741263','[6250, 6256, 6254, 6263, 6259, 6264, 6239, 6267, 6266, 6281, 6274, 6272, 6275, 6244, 6257]',0);
CREATE TABLE IF NOT EXISTS "Token" (
    pk INTEGER NOT NULL,
    jti VARCHAR(36) NOT NULL,
    token_type INTEGER NOT NULL,
    username VARCHAR(32) NOT NULL,
    user_pk INTEGER,
    created DATETIME DEFAULT (CURRENT_TIMESTAMP) NOT NULL,
    expires DATETIME,
    revoked BOOLEAN NOT NULL,
    PRIMARY KEY (pk),
    FOREIGN KEY(user_pk) REFERENCES "User" (pk),
    CHECK (revoked IN (0, 1))
);
CREATE TABLE IF NOT EXISTS "Track" (
    pk INTEGER NOT NULL,
    number INTEGER NOT NULL,
    start_time INTEGER NOT NULL,
    game INTEGER NOT NULL,
    song INTEGER NOT NULL,
    PRIMARY KEY (pk),
    UNIQUE (number, game),
    FOREIGN KEY(game) REFERENCES "Game" (pk),
    FOREIGN KEY(song) REFERENCES "Song" (pk)
);
INSERT INTO Track VALUES(1,0,9048,1,49);
INSERT INTO Track VALUES(2,1,39072,1,34);
INSERT INTO Track VALUES(3,2,69096,1,7);
INSERT INTO Track VALUES(4,3,94287,1,41);
INSERT INTO Track VALUES(5,4,124311,1,28);
INSERT INTO Track VALUES(6,5,154335,1,10);
INSERT INTO Track VALUES(7,6,184359,1,2);
INSERT INTO Track VALUES(8,7,214383,1,9);
INSERT INTO Track VALUES(9,8,244407,1,63);
INSERT INTO Track VALUES(10,9,274431,1,56);
INSERT INTO Track VALUES(11,10,304455,1,59);
INSERT INTO Track VALUES(12,11,334479,1,20);
INSERT INTO Track VALUES(13,12,364503,1,60);
INSERT INTO Track VALUES(14,13,394527,1,18);
INSERT INTO Track VALUES(15,14,424551,1,71);
INSERT INTO Track VALUES(16,15,454575,1,13);
INSERT INTO Track VALUES(17,16,484599,1,33);
INSERT INTO Track VALUES(18,17,514623,1,54);
INSERT INTO Track VALUES(19,18,544647,1,21);
INSERT INTO Track VALUES(20,19,574671,1,8);
INSERT INTO Track VALUES(21,20,604695,1,55);
INSERT INTO Track VALUES(22,21,634719,1,61);
INSERT INTO Track VALUES(23,22,664743,1,14);
INSERT INTO Track VALUES(24,23,694767,1,22);
INSERT INTO Track VALUES(25,24,724791,1,62);
INSERT INTO Track VALUES(26,25,754815,1,1);
INSERT INTO Track VALUES(27,26,784839,1,66);
INSERT INTO Track VALUES(28,27,807836,1,15);
INSERT INTO Track VALUES(29,28,837860,1,23);
INSERT INTO Track VALUES(30,29,867884,1,69);
INSERT INTO Track VALUES(31,30,897908,1,32);
INSERT INTO Track VALUES(32,31,927932,1,31);
INSERT INTO Track VALUES(33,32,957956,1,38);
INSERT INTO Track VALUES(34,33,987980,1,27);
INSERT INTO Track VALUES(35,34,1018004,1,17);
INSERT INTO Track VALUES(36,35,1048028,1,67);
INSERT INTO Track VALUES(37,36,1059688,1,19);
INSERT INTO Track VALUES(38,37,1089712,1,4);
INSERT INTO Track VALUES(39,38,1119736,1,64);
INSERT INTO Track VALUES(40,39,1149760,1,11);
INSERT INTO Track VALUES(41,40,1179784,1,26);
INSERT INTO Track VALUES(42,41,1209808,1,43);
INSERT INTO Track VALUES(43,42,1239832,1,29);
INSERT INTO Track VALUES(44,43,1269856,1,46);
INSERT INTO Track VALUES(45,44,1299880,1,50);
INSERT INTO Track VALUES(46,45,1329904,1,37);
INSERT INTO Track VALUES(47,46,1359928,1,36);
INSERT INTO Track VALUES(48,47,1389952,1,16);
INSERT INTO Track VALUES(49,48,1419976,1,3);
INSERT INTO Track VALUES(50,49,1450000,1,35);
CREATE TABLE IF NOT EXISTS "BingoTicket_Track" (
    bingoticket INTEGER NOT NULL,
    track INTEGER NOT NULL,
    PRIMARY KEY (bingoticket, track),
    FOREIGN KEY(bingoticket) REFERENCES "BingoTicket" (pk),
    FOREIGN KEY(track) REFERENCES "Track" (pk)
);
INSERT INTO BingoTicket_Track VALUES(1,6);
INSERT INTO BingoTicket_Track VALUES(1,9);
INSERT INTO BingoTicket_Track VALUES(1,10);
INSERT INTO BingoTicket_Track VALUES(1,12);
INSERT INTO BingoTicket_Track VALUES(1,20);
INSERT INTO BingoTicket_Track VALUES(1,24);
INSERT INTO BingoTicket_Track VALUES(1,27);
INSERT INTO BingoTicket_Track VALUES(1,28);
INSERT INTO BingoTicket_Track VALUES(1,32);
INSERT INTO BingoTicket_Track VALUES(1,39);
INSERT INTO BingoTicket_Track VALUES(1,41);
INSERT INTO BingoTicket_Track VALUES(1,42);
INSERT INTO BingoTicket_Track VALUES(1,43);
INSERT INTO BingoTicket_Track VALUES(1,46);
INSERT INTO BingoTicket_Track VALUES(1,50);
INSERT INTO BingoTicket_Track VALUES(2,3);
INSERT INTO BingoTicket_Track VALUES(2,7);
INSERT INTO BingoTicket_Track VALUES(2,8);
INSERT INTO BingoTicket_Track VALUES(2,10);
INSERT INTO BingoTicket_Track VALUES(2,12);
INSERT INTO BingoTicket_Track VALUES(2,14);
INSERT INTO BingoTicket_Track VALUES(2,15);
INSERT INTO BingoTicket_Track VALUES(2,20);
INSERT INTO BingoTicket_Track VALUES(2,22);
INSERT INTO BingoTicket_Track VALUES(2,23);
INSERT INTO BingoTicket_Track VALUES(2,30);
INSERT INTO BingoTicket_Track VALUES(2,39);
INSERT INTO BingoTicket_Track VALUES(2,43);
INSERT INTO BingoTicket_Track VALUES(2,47);
INSERT INTO BingoTicket_Track VALUES(2,50);
INSERT INTO BingoTicket_Track VALUES(3,6);
INSERT INTO BingoTicket_Track VALUES(3,13);
INSERT INTO BingoTicket_Track VALUES(3,14);
INSERT INTO BingoTicket_Track VALUES(3,20);
INSERT INTO BingoTicket_Track VALUES(3,26);
INSERT INTO BingoTicket_Track VALUES(3,28);
INSERT INTO BingoTicket_Track VALUES(3,30);
INSERT INTO BingoTicket_Track VALUES(3,33);
INSERT INTO BingoTicket_Track VALUES(3,39);
INSERT INTO BingoTicket_Track VALUES(3,40);
INSERT INTO BingoTicket_Track VALUES(3,44);
INSERT INTO BingoTicket_Track VALUES(3,45);
INSERT INTO BingoTicket_Track VALUES(3,46);
INSERT INTO BingoTicket_Track VALUES(3,49);
INSERT INTO BingoTicket_Track VALUES(3,50);
INSERT INTO BingoTicket_Track VALUES(4,3);
INSERT INTO BingoTicket_Track VALUES(4,4);
INSERT INTO BingoTicket_Track VALUES(4,8);
INSERT INTO BingoTicket_Track VALUES(4,14);
INSERT INTO BingoTicket_Track VALUES(4,15);
INSERT INTO BingoTicket_Track VALUES(4,20);
INSERT INTO BingoTicket_Track VALUES(4,22);
INSERT INTO BingoTicket_Track VALUES(4,28);
INSERT INTO BingoTicket_Track VALUES(4,29);
INSERT INTO BingoTicket_Track VALUES(4,39);
INSERT INTO BingoTicket_Track VALUES(4,40);
INSERT INTO BingoTicket_Track VALUES(4,41);
INSERT INTO BingoTicket_Track VALUES(4,42);
INSERT INTO BingoTicket_Track VALUES(4,47);
INSERT INTO BingoTicket_Track VALUES(4,50);
INSERT INTO BingoTicket_Track VALUES(5,2);
INSERT INTO BingoTicket_Track VALUES(5,10);
INSERT INTO BingoTicket_Track VALUES(5,15);
INSERT INTO BingoTicket_Track VALUES(5,22);
INSERT INTO BingoTicket_Track VALUES(5,28);
INSERT INTO BingoTicket_Track VALUES(5,29);
INSERT INTO BingoTicket_Track VALUES(5,31);
INSERT INTO BingoTicket_Track VALUES(5,32);
INSERT INTO BingoTicket_Track VALUES(5,33);
INSERT INTO BingoTicket_Track VALUES(5,34);
INSERT INTO BingoTicket_Track VALUES(5,41);
INSERT INTO BingoTicket_Track VALUES(5,44);
INSERT INTO BingoTicket_Track VALUES(5,45);
INSERT INTO BingoTicket_Track VALUES(5,47);
INSERT INTO BingoTicket_Track VALUES(5,50);
INSERT INTO BingoTicket_Track VALUES(6,1);
INSERT INTO BingoTicket_Track VALUES(6,5);
INSERT INTO BingoTicket_Track VALUES(6,6);
INSERT INTO BingoTicket_Track VALUES(6,7);
INSERT INTO BingoTicket_Track VALUES(6,12);
INSERT INTO BingoTicket_Track VALUES(6,18);
INSERT INTO BingoTicket_Track VALUES(6,19);
INSERT INTO BingoTicket_Track VALUES(6,20);
INSERT INTO BingoTicket_Track VALUES(6,23);
INSERT INTO BingoTicket_Track VALUES(6,28);
INSERT INTO BingoTicket_Track VALUES(6,32);
INSERT INTO BingoTicket_Track VALUES(6,33);
INSERT INTO BingoTicket_Track VALUES(6,39);
INSERT INTO BingoTicket_Track VALUES(6,42);
INSERT INTO BingoTicket_Track VALUES(6,48);
INSERT INTO BingoTicket_Track VALUES(7,2);
INSERT INTO BingoTicket_Track VALUES(7,5);
INSERT INTO BingoTicket_Track VALUES(7,9);
INSERT INTO BingoTicket_Track VALUES(7,14);
INSERT INTO BingoTicket_Track VALUES(7,15);
INSERT INTO BingoTicket_Track VALUES(7,17);
INSERT INTO BingoTicket_Track VALUES(7,19);
INSERT INTO BingoTicket_Track VALUES(7,23);
INSERT INTO BingoTicket_Track VALUES(7,24);
INSERT INTO BingoTicket_Track VALUES(7,28);
INSERT INTO BingoTicket_Track VALUES(7,34);
INSERT INTO BingoTicket_Track VALUES(7,36);
INSERT INTO BingoTicket_Track VALUES(7,38);
INSERT INTO BingoTicket_Track VALUES(7,41);
INSERT INTO BingoTicket_Track VALUES(7,45);
INSERT INTO BingoTicket_Track VALUES(8,7);
INSERT INTO BingoTicket_Track VALUES(8,10);
INSERT INTO BingoTicket_Track VALUES(8,12);
INSERT INTO BingoTicket_Track VALUES(8,17);
INSERT INTO BingoTicket_Track VALUES(8,24);
INSERT INTO BingoTicket_Track VALUES(8,25);
INSERT INTO BingoTicket_Track VALUES(8,28);
INSERT INTO BingoTicket_Track VALUES(8,30);
INSERT INTO BingoTicket_Track VALUES(8,31);
INSERT INTO BingoTicket_Track VALUES(8,35);
INSERT INTO BingoTicket_Track VALUES(8,37);
INSERT INTO BingoTicket_Track VALUES(8,38);
INSERT INTO BingoTicket_Track VALUES(8,40);
INSERT INTO BingoTicket_Track VALUES(8,41);
INSERT INTO BingoTicket_Track VALUES(8,49);
INSERT INTO BingoTicket_Track VALUES(9,4);
INSERT INTO BingoTicket_Track VALUES(9,7);
INSERT INTO BingoTicket_Track VALUES(9,10);
INSERT INTO BingoTicket_Track VALUES(9,11);
INSERT INTO BingoTicket_Track VALUES(9,15);
INSERT INTO BingoTicket_Track VALUES(9,16);
INSERT INTO BingoTicket_Track VALUES(9,21);
INSERT INTO BingoTicket_Track VALUES(9,22);
INSERT INTO BingoTicket_Track VALUES(9,33);
INSERT INTO BingoTicket_Track VALUES(9,36);
INSERT INTO BingoTicket_Track VALUES(9,39);
INSERT INTO BingoTicket_Track VALUES(9,40);
INSERT INTO BingoTicket_Track VALUES(9,41);
INSERT INTO BingoTicket_Track VALUES(9,42);
INSERT INTO BingoTicket_Track VALUES(9,44);
INSERT INTO BingoTicket_Track VALUES(10,3);
INSERT INTO BingoTicket_Track VALUES(10,14);
INSERT INTO BingoTicket_Track VALUES(10,19);
INSERT INTO BingoTicket_Track VALUES(10,22);
INSERT INTO BingoTicket_Track VALUES(10,23);
INSERT INTO BingoTicket_Track VALUES(10,24);
INSERT INTO BingoTicket_Track VALUES(10,25);
INSERT INTO BingoTicket_Track VALUES(10,28);
INSERT INTO BingoTicket_Track VALUES(10,35);
INSERT INTO BingoTicket_Track VALUES(10,37);
INSERT INTO BingoTicket_Track VALUES(10,39);
INSERT INTO BingoTicket_Track VALUES(10,40);
INSERT INTO BingoTicket_Track VALUES(10,41);
INSERT INTO BingoTicket_Track VALUES(10,49);
INSERT INTO BingoTicket_Track VALUES(10,50);
INSERT INTO BingoTicket_Track VALUES(11,6);
INSERT INTO BingoTicket_Track VALUES(11,10);
INSERT INTO BingoTicket_Track VALUES(11,14);
INSERT INTO BingoTicket_Track VALUES(11,19);
INSERT INTO BingoTicket_Track VALUES(11,21);
INSERT INTO BingoTicket_Track VALUES(11,23);
INSERT INTO BingoTicket_Track VALUES(11,24);
INSERT INTO BingoTicket_Track VALUES(11,25);
INSERT INTO BingoTicket_Track VALUES(11,29);
INSERT INTO BingoTicket_Track VALUES(11,32);
INSERT INTO BingoTicket_Track VALUES(11,35);
INSERT INTO BingoTicket_Track VALUES(11,39);
INSERT INTO BingoTicket_Track VALUES(11,40);
INSERT INTO BingoTicket_Track VALUES(11,49);
INSERT INTO BingoTicket_Track VALUES(11,50);
INSERT INTO BingoTicket_Track VALUES(12,2);
INSERT INTO BingoTicket_Track VALUES(12,3);
INSERT INTO BingoTicket_Track VALUES(12,5);
INSERT INTO BingoTicket_Track VALUES(12,8);
INSERT INTO BingoTicket_Track VALUES(12,9);
INSERT INTO BingoTicket_Track VALUES(12,10);
INSERT INTO BingoTicket_Track VALUES(12,11);
INSERT INTO BingoTicket_Track VALUES(12,15);
INSERT INTO BingoTicket_Track VALUES(12,23);
INSERT INTO BingoTicket_Track VALUES(12,27);
INSERT INTO BingoTicket_Track VALUES(12,32);
INSERT INTO BingoTicket_Track VALUES(12,39);
INSERT INTO BingoTicket_Track VALUES(12,45);
INSERT INTO BingoTicket_Track VALUES(12,48);
INSERT INTO BingoTicket_Track VALUES(12,49);
INSERT INTO BingoTicket_Track VALUES(13,5);
INSERT INTO BingoTicket_Track VALUES(13,7);
INSERT INTO BingoTicket_Track VALUES(13,8);
INSERT INTO BingoTicket_Track VALUES(13,11);
INSERT INTO BingoTicket_Track VALUES(13,14);
INSERT INTO BingoTicket_Track VALUES(13,20);
INSERT INTO BingoTicket_Track VALUES(13,21);
INSERT INTO BingoTicket_Track VALUES(13,22);
INSERT INTO BingoTicket_Track VALUES(13,23);
INSERT INTO BingoTicket_Track VALUES(13,31);
INSERT INTO BingoTicket_Track VALUES(13,33);
INSERT INTO BingoTicket_Track VALUES(13,36);
INSERT INTO BingoTicket_Track VALUES(13,41);
INSERT INTO BingoTicket_Track VALUES(13,43);
INSERT INTO BingoTicket_Track VALUES(13,49);
INSERT INTO BingoTicket_Track VALUES(14,3);
INSERT INTO BingoTicket_Track VALUES(14,12);
INSERT INTO BingoTicket_Track VALUES(14,14);
INSERT INTO BingoTicket_Track VALUES(14,17);
INSERT INTO BingoTicket_Track VALUES(14,18);
INSERT INTO BingoTicket_Track VALUES(14,19);
INSERT INTO BingoTicket_Track VALUES(14,27);
INSERT INTO BingoTicket_Track VALUES(14,28);
INSERT INTO BingoTicket_Track VALUES(14,31);
INSERT INTO BingoTicket_Track VALUES(14,32);
INSERT INTO BingoTicket_Track VALUES(14,36);
INSERT INTO BingoTicket_Track VALUES(14,39);
INSERT INTO BingoTicket_Track VALUES(14,42);
INSERT INTO BingoTicket_Track VALUES(14,43);
INSERT INTO BingoTicket_Track VALUES(14,47);
INSERT INTO BingoTicket_Track VALUES(15,1);
INSERT INTO BingoTicket_Track VALUES(15,6);
INSERT INTO BingoTicket_Track VALUES(15,10);
INSERT INTO BingoTicket_Track VALUES(15,14);
INSERT INTO BingoTicket_Track VALUES(15,17);
INSERT INTO BingoTicket_Track VALUES(15,22);
INSERT INTO BingoTicket_Track VALUES(15,23);
INSERT INTO BingoTicket_Track VALUES(15,25);
INSERT INTO BingoTicket_Track VALUES(15,30);
INSERT INTO BingoTicket_Track VALUES(15,36);
INSERT INTO BingoTicket_Track VALUES(15,37);
INSERT INTO BingoTicket_Track VALUES(15,39);
INSERT INTO BingoTicket_Track VALUES(15,43);
INSERT INTO BingoTicket_Track VALUES(15,46);
INSERT INTO BingoTicket_Track VALUES(15,50);
INSERT INTO BingoTicket_Track VALUES(16,1);
INSERT INTO BingoTicket_Track VALUES(16,3);
INSERT INTO BingoTicket_Track VALUES(16,5);
INSERT INTO BingoTicket_Track VALUES(16,7);
INSERT INTO BingoTicket_Track VALUES(16,9);
INSERT INTO BingoTicket_Track VALUES(16,15);
INSERT INTO BingoTicket_Track VALUES(16,24);
INSERT INTO BingoTicket_Track VALUES(16,25);
INSERT INTO BingoTicket_Track VALUES(16,32);
INSERT INTO BingoTicket_Track VALUES(16,35);
INSERT INTO BingoTicket_Track VALUES(16,38);
INSERT INTO BingoTicket_Track VALUES(16,46);
INSERT INTO BingoTicket_Track VALUES(16,48);
INSERT INTO BingoTicket_Track VALUES(16,49);
INSERT INTO BingoTicket_Track VALUES(16,50);
INSERT INTO BingoTicket_Track VALUES(17,5);
INSERT INTO BingoTicket_Track VALUES(17,7);
INSERT INTO BingoTicket_Track VALUES(17,10);
INSERT INTO BingoTicket_Track VALUES(17,15);
INSERT INTO BingoTicket_Track VALUES(17,16);
INSERT INTO BingoTicket_Track VALUES(17,17);
INSERT INTO BingoTicket_Track VALUES(17,18);
INSERT INTO BingoTicket_Track VALUES(17,20);
INSERT INTO BingoTicket_Track VALUES(17,23);
INSERT INTO BingoTicket_Track VALUES(17,31);
INSERT INTO BingoTicket_Track VALUES(17,32);
INSERT INTO BingoTicket_Track VALUES(17,38);
INSERT INTO BingoTicket_Track VALUES(17,39);
INSERT INTO BingoTicket_Track VALUES(17,40);
INSERT INTO BingoTicket_Track VALUES(17,50);
INSERT INTO BingoTicket_Track VALUES(18,4);
INSERT INTO BingoTicket_Track VALUES(18,5);
INSERT INTO BingoTicket_Track VALUES(18,7);
INSERT INTO BingoTicket_Track VALUES(18,8);
INSERT INTO BingoTicket_Track VALUES(18,11);
INSERT INTO BingoTicket_Track VALUES(18,13);
INSERT INTO BingoTicket_Track VALUES(18,21);
INSERT INTO BingoTicket_Track VALUES(18,25);
INSERT INTO BingoTicket_Track VALUES(18,27);
INSERT INTO BingoTicket_Track VALUES(18,34);
INSERT INTO BingoTicket_Track VALUES(18,37);
INSERT INTO BingoTicket_Track VALUES(18,41);
INSERT INTO BingoTicket_Track VALUES(18,43);
INSERT INTO BingoTicket_Track VALUES(18,49);
INSERT INTO BingoTicket_Track VALUES(18,50);
INSERT INTO BingoTicket_Track VALUES(19,1);
INSERT INTO BingoTicket_Track VALUES(19,4);
INSERT INTO BingoTicket_Track VALUES(19,9);
INSERT INTO BingoTicket_Track VALUES(19,13);
INSERT INTO BingoTicket_Track VALUES(19,14);
INSERT INTO BingoTicket_Track VALUES(19,18);
INSERT INTO BingoTicket_Track VALUES(19,20);
INSERT INTO BingoTicket_Track VALUES(19,21);
INSERT INTO BingoTicket_Track VALUES(19,25);
INSERT INTO BingoTicket_Track VALUES(19,27);
INSERT INTO BingoTicket_Track VALUES(19,32);
INSERT INTO BingoTicket_Track VALUES(19,37);
INSERT INTO BingoTicket_Track VALUES(19,38);
INSERT INTO BingoTicket_Track VALUES(19,43);
INSERT INTO BingoTicket_Track VALUES(19,46);
INSERT INTO BingoTicket_Track VALUES(20,7);
INSERT INTO BingoTicket_Track VALUES(20,10);
INSERT INTO BingoTicket_Track VALUES(20,11);
INSERT INTO BingoTicket_Track VALUES(20,17);
INSERT INTO BingoTicket_Track VALUES(20,20);
INSERT INTO BingoTicket_Track VALUES(20,27);
INSERT INTO BingoTicket_Track VALUES(20,29);
INSERT INTO BingoTicket_Track VALUES(20,30);
INSERT INTO BingoTicket_Track VALUES(20,33);
INSERT INTO BingoTicket_Track VALUES(20,37);
INSERT INTO BingoTicket_Track VALUES(20,39);
INSERT INTO BingoTicket_Track VALUES(20,40);
INSERT INTO BingoTicket_Track VALUES(20,46);
INSERT INTO BingoTicket_Track VALUES(20,48);
INSERT INTO BingoTicket_Track VALUES(20,50);
INSERT INTO BingoTicket_Track VALUES(21,9);
INSERT INTO BingoTicket_Track VALUES(21,12);
INSERT INTO BingoTicket_Track VALUES(21,16);
INSERT INTO BingoTicket_Track VALUES(21,17);
INSERT INTO BingoTicket_Track VALUES(21,19);
INSERT INTO BingoTicket_Track VALUES(21,22);
INSERT INTO BingoTicket_Track VALUES(21,23);
INSERT INTO BingoTicket_Track VALUES(21,26);
INSERT INTO BingoTicket_Track VALUES(21,30);
INSERT INTO BingoTicket_Track VALUES(21,34);
INSERT INTO BingoTicket_Track VALUES(21,37);
INSERT INTO BingoTicket_Track VALUES(21,44);
INSERT INTO BingoTicket_Track VALUES(21,45);
INSERT INTO BingoTicket_Track VALUES(21,48);
INSERT INTO BingoTicket_Track VALUES(21,50);
INSERT INTO BingoTicket_Track VALUES(22,1);
INSERT INTO BingoTicket_Track VALUES(22,6);
INSERT INTO BingoTicket_Track VALUES(22,10);
INSERT INTO BingoTicket_Track VALUES(22,11);
INSERT INTO BingoTicket_Track VALUES(22,14);
INSERT INTO BingoTicket_Track VALUES(22,19);
INSERT INTO BingoTicket_Track VALUES(22,26);
INSERT INTO BingoTicket_Track VALUES(22,28);
INSERT INTO BingoTicket_Track VALUES(22,35);
INSERT INTO BingoTicket_Track VALUES(22,36);
INSERT INTO BingoTicket_Track VALUES(22,38);
INSERT INTO BingoTicket_Track VALUES(22,41);
INSERT INTO BingoTicket_Track VALUES(22,42);
INSERT INTO BingoTicket_Track VALUES(22,43);
INSERT INTO BingoTicket_Track VALUES(22,49);
INSERT INTO BingoTicket_Track VALUES(23,1);
INSERT INTO BingoTicket_Track VALUES(23,2);
INSERT INTO BingoTicket_Track VALUES(23,14);
INSERT INTO BingoTicket_Track VALUES(23,15);
INSERT INTO BingoTicket_Track VALUES(23,20);
INSERT INTO BingoTicket_Track VALUES(23,22);
INSERT INTO BingoTicket_Track VALUES(23,24);
INSERT INTO BingoTicket_Track VALUES(23,25);
INSERT INTO BingoTicket_Track VALUES(23,28);
INSERT INTO BingoTicket_Track VALUES(23,29);
INSERT INTO BingoTicket_Track VALUES(23,35);
INSERT INTO BingoTicket_Track VALUES(23,40);
INSERT INTO BingoTicket_Track VALUES(23,43);
INSERT INTO BingoTicket_Track VALUES(23,44);
INSERT INTO BingoTicket_Track VALUES(23,50);
INSERT INTO BingoTicket_Track VALUES(24,7);
INSERT INTO BingoTicket_Track VALUES(24,12);
INSERT INTO BingoTicket_Track VALUES(24,18);
INSERT INTO BingoTicket_Track VALUES(24,22);
INSERT INTO BingoTicket_Track VALUES(24,24);
INSERT INTO BingoTicket_Track VALUES(24,25);
INSERT INTO BingoTicket_Track VALUES(24,27);
INSERT INTO BingoTicket_Track VALUES(24,31);
INSERT INTO BingoTicket_Track VALUES(24,32);
INSERT INTO BingoTicket_Track VALUES(24,34);
INSERT INTO BingoTicket_Track VALUES(24,35);
INSERT INTO BingoTicket_Track VALUES(24,40);
INSERT INTO BingoTicket_Track VALUES(24,42);
INSERT INTO BingoTicket_Track VALUES(24,43);
INSERT INTO BingoTicket_Track VALUES(24,49);
CREATE UNIQUE INDEX "ix_Directory_name" ON "Directory" (name);
CREATE INDEX "ix_Song_title" ON "Song" (title);
CREATE INDEX "ix_Song_filename" ON "Song" (filename);
COMMIT;
