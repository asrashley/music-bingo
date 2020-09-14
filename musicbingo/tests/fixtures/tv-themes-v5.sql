PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Directory" (
    pk INTEGER NOT NULL,
    name VARCHAR(512) NOT NULL,
    title VARCHAR(512) NOT NULL,
    artist VARCHAR(512),
    directory INTEGER,
    PRIMARY KEY (pk),
    FOREIGN KEY(directory) REFERENCES "Directory" (pk)
);
INSERT INTO Directory VALUES(1,'Clips/TV Themes','[TV Themes]','',NULL);
CREATE TABLE IF NOT EXISTS "Artist" (
    pk INTEGER NOT NULL,
    name VARCHAR(512),
    PRIMARY KEY (pk)
);
INSERT INTO Artist VALUES(1,'The Monkees');
INSERT INTO Artist VALUES(2,'Dusty Springfield');
INSERT INTO Artist VALUES(3,'Ray Parker Jr');
INSERT INTO Artist VALUES(4,'Johnny Mandel');
INSERT INTO Artist VALUES(5,'Gordon Lorenz Orchestra');
INSERT INTO Artist VALUES(6,'Tom Scott');
INSERT INTO Artist VALUES(7,'Mike Post & Pete Carpenter');
INSERT INTO Artist VALUES(8,'Various Artists');
INSERT INTO Artist VALUES(9,'Gordon Giltrap');
CREATE TABLE IF NOT EXISTS "Game" (
    pk INTEGER NOT NULL,
    id VARCHAR(64) NOT NULL,
    title VARCHAR(256) NOT NULL,
    start DATETIME NOT NULL,
    "end" DATETIME NOT NULL,
    options TEXT,
    PRIMARY KEY (pk),
    UNIQUE (id),
    UNIQUE (start)
);
INSERT INTO Game VALUES(1,'20-04-24-2','TV Themes','2020-04-24 18:05:44.048300','2020-08-02 18:05:44.048300',NULL);
CREATE TABLE IF NOT EXISTS "User" (
    pk INTEGER NOT NULL,
    username VARCHAR(32) NOT NULL,
    password VARCHAR(512) NOT NULL,
    email VARCHAR(256) NOT NULL,
    last_login DATETIME,
    groups_mask INTEGER NOT NULL,
    reset_expires DATETIME,
    reset_token VARCHAR(32),
    PRIMARY KEY (pk),
    UNIQUE (username),
    UNIQUE (email)
);
INSERT INTO User VALUES(1,'admin','$2b$12$H8xhXO1D1t74YL2Ya2s6O.Kw7jGvWQjKci1y4E7L8ZAgrFE2EAanW','admin@music.bingo',NULL,1073741825,NULL,NULL);
INSERT INTO User VALUES(2,'user','$2b$12$CMqbfc75fgPwQYfAsUvqo.x/G7/5uqTAiKKU6/R/MS.6sfyXHmcI2','user@unit.test',NULL,1,'2020-07-09 17:03:51.000000','Ez9o0X53sH_R0Q28JAiwBw');
CREATE TABLE IF NOT EXISTS "Song" (
    pk INTEGER NOT NULL,
    directory INTEGER NOT NULL,
    filename VARCHAR(512) NOT NULL,
    title VARCHAR(512) NOT NULL,
    duration INTEGER NOT NULL,
    channels INTEGER NOT NULL,
    sample_rate INTEGER NOT NULL,
    sample_width INTEGER NOT NULL,
    bitrate INTEGER NOT NULL,
    album VARCHAR(512),
    uuid VARCHAR(22),
    artist_pk INTEGER,
    PRIMARY KEY (pk),
    UNIQUE (directory, filename),
    FOREIGN KEY(directory) REFERENCES "Directory" (pk),
    FOREIGN KEY(artist_pk) REFERENCES "Artist" (pk)
);
INSERT INTO Song VALUES(1,1,'01-25- Ghostbusters.mp3','Ghostbusters',30016,2,44100,16,256,'100 Hits 80s Essentials','IE[95?+sH_Pu^INPg9ka',3);
INSERT INTO Song VALUES(2,1,'02 Match Of The Day.mp3','Match Of The Day',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','BdI(VVoMlkM*)_Z88Rtf',5);
INSERT INTO Song VALUES(3,1,'02 Sex And The City.mp3','Sex And The City',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','B7Nh8:UO.GZ6)Q@ASu[K',8);
INSERT INTO Song VALUES(4,1,'03 Ally McBeal.mp3','Ally McBeal',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','3,/2aOuH>tKb3>rS.5&9',8);
INSERT INTO Song VALUES(5,1,'04 Starsky And Hutch.mp3','Starsky And Hutch',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','C6R_9b>VD5L%$XT#3>T1',6);
INSERT INTO Song VALUES(6,1,'04 Will & Grace.mp3','Will & Grace',27639,2,44100,16,257,'All-Time Top 100 TV Themes [Disc 1]','nn@4o$"[&8]l_$F$\:3;',8);
INSERT INTO Song VALUES(7,1,'05 A Question Of Sport.mp3','A Question Of Sport',25183,2,44100,16,257,'Your 101 All Time Favourite TV Themes','>`5_4ejWX@K3p.!(;6+g',5);
INSERT INTO Song VALUES(8,1,'06 Frasier.mp3','Frasier',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','L#f6Ul??I*XbZ<oXT.:,',8);
INSERT INTO Song VALUES(9,1,'07 Friends.mp3','Friends',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','N[f4]1e^gLN@tnF<#uf\',8);
INSERT INTO Song VALUES(10,1,'07 Ski Sunday (Pop Looks Bach).mp3','Ski Sunday',30016,2,44100,16,257,'Your 101 All Time Favourite TV Themes','1I9a-2,@I1NQdB+!MRIm',5);
INSERT INTO Song VALUES(11,1,'08 Dangermouse.mp3','Dangermouse',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','>O0)MS\/4^SZgRSG79r/',5);
INSERT INTO Song VALUES(12,1,'08 The Rockford Files.mp3','The Rockford Files',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','KaSo;pbH$<XrJijiTUVA',7);
INSERT INTO Song VALUES(13,1,'09 Doctor Who.mp3','Doctor Who',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','Bo9<<J&G5>Su4U^TXZ5J',5);
INSERT INTO Song VALUES(14,1,'10 The Six Million Dollar Man.mp3','The Six Million Dollar Man',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','.opQ.nJbc"K!"RUCq6p,',2);
INSERT INTO Song VALUES(15,1,'11 M-A-S-H.mp3','M*A*S*H',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]',':?''.NjdT22YM:S:j<0i-',4);
INSERT INTO Song VALUES(16,1,'12 The Waltons.mp3','The Waltons',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','TW28C>mjfVPj4%P]S]L''',8);
INSERT INTO Song VALUES(17,1,'14 Black Beauty.mp3','Black Beauty',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','@^:/mhWn4pNEJeAQ/o9/',5);
INSERT INTO Song VALUES(18,1,'14 The Simpsons.mp3','The Simpsons',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','n-_ccV?U0DJsLXM(*''ej',8);
INSERT INTO Song VALUES(19,1,'15 Home And Away.mp3','Home And Away',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','+icrY._Am5N8cQAj-+oj',5);
INSERT INTO Song VALUES(20,1,'15 thirtysomething.mp3','thirtysomething',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','P?trqoK69\J^\m3L)62(',8);
INSERT INTO Song VALUES(21,1,'15 Thunderbirds.mp3','Thunderbirds',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','Z<MhR''T$.`S0`Bgo+_bZ',5);
INSERT INTO Song VALUES(22,1,'16 Dogtanian.mp3','Dogtanian',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','gK2kOgXoT?PRVh#aA''Rc',5);
INSERT INTO Song VALUES(23,1,'17 The Odd Couple.mp3','The Odd Couple',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','#_m^fG]m9SOLDC);ZWSt',8);
INSERT INTO Song VALUES(24,1,'18 Blockbusters.mp3','Blockbusters',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','\loVViu).OX$-OQbgmcT',5);
INSERT INTO Song VALUES(25,1,'18 L.A. Law.mp3','L.A. Law',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','$]7GdU=rUZWaon31+(3f',8);
INSERT INTO Song VALUES(26,1,'18 Neighbours.mp3','Neighbours',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','B,H-o@mOI+]TUl>]>S,D',5);
INSERT INTO Song VALUES(27,1,'19 Happy Days.mp3','Happy Days',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','$b@R[Rs@l?ObB/GCosP!',8);
INSERT INTO Song VALUES(28,1,'19 Paddington Bear.mp3','Paddington Bear',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','VX$WE?-uM-Z7-7Z%@WG9',5);
INSERT INTO Song VALUES(29,1,'20 Pink Panther.mp3','Pink Panther',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','jk26Hd,n/]Z!QOU=Ce@b',5);
INSERT INTO Song VALUES(30,1,'20 Sesame Street.mp3','Sesame Street',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','1UE4]E=,X8Sns*QdW)4A',8);
INSERT INTO Song VALUES(31,1,'20 The X Files.mp3','The X Files',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','3#Q6ECggH*W[tmMe#TRm',5);
INSERT INTO Song VALUES(32,1,'21 Star Trek.mp3','Star Trek',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','dBXSm9ghp\N]%[5H?jaO',5);
INSERT INTO Song VALUES(33,1,'22 Moonlighting.mp3','Moonlighting',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','IlR=\+/Ds\JbnC[ICi.O',8);
INSERT INTO Song VALUES(34,1,'22 Snooker (Drag Racer).mp3','Snooker',30016,2,44100,16,257,'Your 101 All Time Favourite TV Themes','2M$q5]8p#''LX.\cIYG+]',5);
INSERT INTO Song VALUES(35,1,'24 Blackadder.mp3','Blackadder',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','-g^=<'':MghQS/=-.ELo>',5);
INSERT INTO Song VALUES(36,1,'24 Miami Vice.mp3','Miami Vice',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','s)PNd?u&]lV[;=iI<)"S',8);
INSERT INTO Song VALUES(37,1,'24 Scooby-Doo.mp3','Scooby-Doo',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]',':g@8B*lq5qN]-(--2.SR',8);
INSERT INTO Song VALUES(38,1,'25 Cricket (Soul Limbo).mp3','Cricket',30016,2,44100,16,257,'Your 101 All Time Favourite TV Themes','!TNTt8d\YAREL]/aR/$(',5);
INSERT INTO Song VALUES(39,1,'25 Hawaii Five-0.mp3','Hawaii Five-0',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','-:@4&8r[05ZLs9T1WSH0',8);
INSERT INTO Song VALUES(40,1,'25 Monty Python''s Flying Circus (The Liberty Bell).mp3','Monty Python''s Flying Circus',30016,2,44100,16,257,'Your 101 All Time Favourite TV Themes','<Q[0u=e]7FXcQW=+!oBG',5);
INSERT INTO Song VALUES(41,1,'26 The A-Team.mp3','The A-Team',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','GVu''*98?G(M6Is2olbcA',8);
INSERT INTO Song VALUES(42,1,'26 The Banana Splits.mp3','The Banana Splits',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','dnY(94"4?BVlg<++c^RM',8);
INSERT INTO Song VALUES(43,1,'27 Brookside.mp3','Brookside',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','/X9s[[iep(W%bhJf0)-,',5);
INSERT INTO Song VALUES(44,1,'28 Cheers.mp3','Cheers',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','$0)+)*6qaU[@KkD&Sn6/',8);
INSERT INTO Song VALUES(45,1,'28 Coronation Street.mp3','Coronation Street',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','Xr=HhX%cV`Tq\3m_:q&5',5);
INSERT INTO Song VALUES(46,1,'28 Grand Prix.mp3','Grand Prix',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','EVsu$N+ZB(U[tV%oW%c;',5);
INSERT INTO Song VALUES(47,1,'29 Horse Of The Year.mp3','Horse Of The Year',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','B8W)0Ge@)<Qj)8bEU6/8',5);
INSERT INTO Song VALUES(48,1,'29 Knight Rider.mp3','Knight Rider',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','hdS<G8>f<[\c5Ks,NYXm',8);
INSERT INTO Song VALUES(49,1,'29 The Monkees.mp3','The Monkees',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','SD%DjQ*=/p[,JACBBhhF',1);
INSERT INTO Song VALUES(50,1,'30 Batman.mp3','Batman',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','cEq`a/^dQcX=/)[kZpKl',8);
INSERT INTO Song VALUES(51,1,'30 Cagney & Lacey.mp3','Cagney & Lacey',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','&5o[:Er0,S]%]HkF6i</',8);
INSERT INTO Song VALUES(52,1,'32 Hill Street Blues.mp3','Hill Street Blues',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','i3#BZ6LS37W_)>`/R''W=',8);
INSERT INTO Song VALUES(53,1,'33 Emmerdale.mp3','Emmerdale',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','\OJ4ifY(R4]7a8Uh#b[d',5);
INSERT INTO Song VALUES(54,1,'34 Magnum, P.I.mp3','Magnum, P.I.',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','grCda-&bis[g0j)%SMM8',8);
INSERT INTO Song VALUES(55,1,'35 The Addams Family.mp3','The Addams Family',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','O:dmEPX/Z2M0="#0#,)u',8);
INSERT INTO Song VALUES(56,1,'36 Diff''rent Strokes.mp3','Diff''rent Strokes',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','!Q^itS"3@uReajY0j+[a',8);
INSERT INTO Song VALUES(57,1,'38 Bergerac.mp3','Bergerac',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','WnZtQ/sB+*N$-!M!-m"t',5);
INSERT INTO Song VALUES(58,1,'38 Taxi.mp3','Taxi',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','9.hNKac''BlVNI$dru6A$',8);
INSERT INTO Song VALUES(59,1,'39 Dallas.mp3','Dallas',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','`?IWQ6&/<2W48(fJ@Eg=',8);
INSERT INTO Song VALUES(60,1,'40 The Flintstones.mp3','The Flintstones',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 2]','*gFSs*N322Z<>"kQoJ]S',8);
INSERT INTO Song VALUES(61,1,'41 The Love Boat.mp3','The Love Boat',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','+JNVb!Rss]\,ML^T7L=a',8);
INSERT INTO Song VALUES(62,1,'45 Wonder Woman.mp3','Wonder Woman',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','o9G=G)dud3XH2hUk+g>D',8);
INSERT INTO Song VALUES(63,1,'46 Charlie''s Angels.mp3','Charlie''s Angels',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','kCf0fIaqQuXhf?hRW8?s',8);
INSERT INTO Song VALUES(64,1,'46 Men Behaving Badly.mp3','Men Behaving Badly',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','N?;Hp3DNl-^''NGc2P(J]',5);
INSERT INTO Song VALUES(65,1,'46 Steptoe And Son.mp3','Steptoe And Son',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','(K:^a2S`7QRtZgc]0''$*',5);
INSERT INTO Song VALUES(66,1,'47 Fawlty Towers.mp3','Fawlty Towers',22989,2,44100,16,257,'Your 101 All Time Favourite TV Themes','#q#$!k>58DO;]>6("1Cl',5);
INSERT INTO Song VALUES(67,1,'47 Looney Tunes.mp3','Looney Tunes',11652,2,44100,16,257,'All-Time Top 100 TV Themes [Disc 2]','E;[@\`;NrbO/I#`<c''BP',8);
INSERT INTO Song VALUES(68,1,'47 The Muppet Show.mp3','The Muppet Show',30016,2,44100,16,256,'All-Time Top 100 TV Themes [Disc 1]','Qp(0CB3AE"S4rm5p!t3L',8);
INSERT INTO Song VALUES(69,1,'48 The Sweeney.mp3','The Sweeney',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','4`SD@J<jP2Jj)(=S&b$`',5);
INSERT INTO Song VALUES(70,1,'50 Porridge.mp3','Porridge',30016,2,44100,16,256,'Your 101 All Time Favourite TV Themes','$b*2T9fua_NQ2rNk"XOr',5);
INSERT INTO Song VALUES(71,1,'Wish You Were Here.mp3','Wish You Were Here (The Carnival)',30016,2,44100,16,257,'100 Hits  Guitar Heroes Disc 4','s82PbfJ-U_MR6B[9VmXO',9);
CREATE TABLE IF NOT EXISTS "BingoTicket" (
    pk INTEGER NOT NULL,
    user INTEGER,
    game INTEGER NOT NULL,
    number INTEGER NOT NULL,
    fingerprint VARCHAR(128) NOT NULL,
    checked BIGINT NOT NULL,
    PRIMARY KEY (pk),
    UNIQUE (game, number),
    FOREIGN KEY(user) REFERENCES "User" (pk),
    FOREIGN KEY(game) REFERENCES "Game" (pk)
);
INSERT INTO BingoTicket VALUES(1,NULL,1,1,'137842000276547756267607297119',0);
INSERT INTO BingoTicket VALUES(2,NULL,1,9,'283954211299785196597543535',0);
INSERT INTO BingoTicket VALUES(3,NULL,1,17,'3093561119661660795158752469521',0);
INSERT INTO BingoTicket VALUES(4,NULL,1,2,'3976452437590616476533328505',0);
INSERT INTO BingoTicket VALUES(5,NULL,1,10,'392517808361938290505320193983',0);
INSERT INTO BingoTicket VALUES(6,NULL,1,18,'56083267314458093539386986',0);
INSERT INTO BingoTicket VALUES(7,NULL,1,3,'578209721924019749968315923',0);
INSERT INTO BingoTicket VALUES(8,NULL,1,11,'382407899075551600600660449409',0);
INSERT INTO BingoTicket VALUES(9,NULL,1,19,'5743535842924635965947835083',0);
INSERT INTO BingoTicket VALUES(10,NULL,1,4,'548689728794393997483166514285',0);
INSERT INTO BingoTicket VALUES(11,NULL,1,12,'181532871627159486833217619957',0);
INSERT INTO BingoTicket VALUES(12,NULL,1,20,'5682284329918661534183565',0);
INSERT INTO BingoTicket VALUES(13,NULL,1,5,'3281899216632339278903953993',0);
INSERT INTO BingoTicket VALUES(14,NULL,1,13,'64696482373920204551500973935',0);
INSERT INTO BingoTicket VALUES(15,NULL,1,21,'4737641249456067650221359914',0);
INSERT INTO BingoTicket VALUES(16,NULL,1,6,'128083589153059696336631770',0);
INSERT INTO BingoTicket VALUES(17,NULL,1,14,'5140345345837677997220184359',0);
INSERT INTO BingoTicket VALUES(18,NULL,1,22,'894196174524236874124536163',0);
INSERT INTO BingoTicket VALUES(19,NULL,1,7,'228493148981335956743925382',0);
INSERT INTO BingoTicket VALUES(20,NULL,1,15,'512905498954167636910315247599',0);
INSERT INTO BingoTicket VALUES(21,NULL,1,23,'565347632972216757686486426759',0);
INSERT INTO BingoTicket VALUES(22,NULL,1,8,'3749066119782370711926027478',0);
INSERT INTO BingoTicket VALUES(23,NULL,1,16,'1490162226947038795387715094',0);
INSERT INTO BingoTicket VALUES(24,NULL,1,24,'1260859006682829152811909741263',0);
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
    "order" INTEGER NOT NULL,
    PRIMARY KEY (bingoticket, track),
    FOREIGN KEY(bingoticket) REFERENCES "BingoTicket" (pk),
    FOREIGN KEY(track) REFERENCES "Track" (pk)
);
INSERT INTO BingoTicket_Track VALUES(1,6,0);
INSERT INTO BingoTicket_Track VALUES(1,9,1);
INSERT INTO BingoTicket_Track VALUES(1,10,2);
INSERT INTO BingoTicket_Track VALUES(1,12,3);
INSERT INTO BingoTicket_Track VALUES(1,20,4);
INSERT INTO BingoTicket_Track VALUES(1,24,5);
INSERT INTO BingoTicket_Track VALUES(1,27,6);
INSERT INTO BingoTicket_Track VALUES(1,28,7);
INSERT INTO BingoTicket_Track VALUES(1,32,8);
INSERT INTO BingoTicket_Track VALUES(1,39,9);
INSERT INTO BingoTicket_Track VALUES(1,41,10);
INSERT INTO BingoTicket_Track VALUES(1,42,11);
INSERT INTO BingoTicket_Track VALUES(1,43,12);
INSERT INTO BingoTicket_Track VALUES(1,46,13);
INSERT INTO BingoTicket_Track VALUES(1,50,14);
INSERT INTO BingoTicket_Track VALUES(2,3,0);
INSERT INTO BingoTicket_Track VALUES(2,7,1);
INSERT INTO BingoTicket_Track VALUES(2,8,2);
INSERT INTO BingoTicket_Track VALUES(2,10,3);
INSERT INTO BingoTicket_Track VALUES(2,12,4);
INSERT INTO BingoTicket_Track VALUES(2,14,5);
INSERT INTO BingoTicket_Track VALUES(2,15,6);
INSERT INTO BingoTicket_Track VALUES(2,20,7);
INSERT INTO BingoTicket_Track VALUES(2,22,8);
INSERT INTO BingoTicket_Track VALUES(2,23,9);
INSERT INTO BingoTicket_Track VALUES(2,30,10);
INSERT INTO BingoTicket_Track VALUES(2,39,11);
INSERT INTO BingoTicket_Track VALUES(2,43,12);
INSERT INTO BingoTicket_Track VALUES(2,47,13);
INSERT INTO BingoTicket_Track VALUES(2,50,14);
INSERT INTO BingoTicket_Track VALUES(3,6,0);
INSERT INTO BingoTicket_Track VALUES(3,13,1);
INSERT INTO BingoTicket_Track VALUES(3,14,2);
INSERT INTO BingoTicket_Track VALUES(3,20,3);
INSERT INTO BingoTicket_Track VALUES(3,26,4);
INSERT INTO BingoTicket_Track VALUES(3,28,5);
INSERT INTO BingoTicket_Track VALUES(3,30,6);
INSERT INTO BingoTicket_Track VALUES(3,33,7);
INSERT INTO BingoTicket_Track VALUES(3,39,8);
INSERT INTO BingoTicket_Track VALUES(3,40,9);
INSERT INTO BingoTicket_Track VALUES(3,44,10);
INSERT INTO BingoTicket_Track VALUES(3,45,11);
INSERT INTO BingoTicket_Track VALUES(3,46,12);
INSERT INTO BingoTicket_Track VALUES(3,49,13);
INSERT INTO BingoTicket_Track VALUES(3,50,14);
INSERT INTO BingoTicket_Track VALUES(4,3,0);
INSERT INTO BingoTicket_Track VALUES(4,4,1);
INSERT INTO BingoTicket_Track VALUES(4,8,2);
INSERT INTO BingoTicket_Track VALUES(4,14,3);
INSERT INTO BingoTicket_Track VALUES(4,15,4);
INSERT INTO BingoTicket_Track VALUES(4,20,5);
INSERT INTO BingoTicket_Track VALUES(4,22,6);
INSERT INTO BingoTicket_Track VALUES(4,28,7);
INSERT INTO BingoTicket_Track VALUES(4,29,8);
INSERT INTO BingoTicket_Track VALUES(4,39,9);
INSERT INTO BingoTicket_Track VALUES(4,40,10);
INSERT INTO BingoTicket_Track VALUES(4,41,11);
INSERT INTO BingoTicket_Track VALUES(4,42,12);
INSERT INTO BingoTicket_Track VALUES(4,47,13);
INSERT INTO BingoTicket_Track VALUES(4,50,14);
INSERT INTO BingoTicket_Track VALUES(5,2,0);
INSERT INTO BingoTicket_Track VALUES(5,10,1);
INSERT INTO BingoTicket_Track VALUES(5,15,2);
INSERT INTO BingoTicket_Track VALUES(5,22,3);
INSERT INTO BingoTicket_Track VALUES(5,28,4);
INSERT INTO BingoTicket_Track VALUES(5,29,5);
INSERT INTO BingoTicket_Track VALUES(5,31,6);
INSERT INTO BingoTicket_Track VALUES(5,32,7);
INSERT INTO BingoTicket_Track VALUES(5,33,8);
INSERT INTO BingoTicket_Track VALUES(5,34,9);
INSERT INTO BingoTicket_Track VALUES(5,41,10);
INSERT INTO BingoTicket_Track VALUES(5,44,11);
INSERT INTO BingoTicket_Track VALUES(5,45,12);
INSERT INTO BingoTicket_Track VALUES(5,47,13);
INSERT INTO BingoTicket_Track VALUES(5,50,14);
INSERT INTO BingoTicket_Track VALUES(6,1,0);
INSERT INTO BingoTicket_Track VALUES(6,5,1);
INSERT INTO BingoTicket_Track VALUES(6,6,2);
INSERT INTO BingoTicket_Track VALUES(6,7,3);
INSERT INTO BingoTicket_Track VALUES(6,12,4);
INSERT INTO BingoTicket_Track VALUES(6,18,5);
INSERT INTO BingoTicket_Track VALUES(6,19,6);
INSERT INTO BingoTicket_Track VALUES(6,20,7);
INSERT INTO BingoTicket_Track VALUES(6,23,8);
INSERT INTO BingoTicket_Track VALUES(6,28,9);
INSERT INTO BingoTicket_Track VALUES(6,32,10);
INSERT INTO BingoTicket_Track VALUES(6,33,11);
INSERT INTO BingoTicket_Track VALUES(6,39,12);
INSERT INTO BingoTicket_Track VALUES(6,42,13);
INSERT INTO BingoTicket_Track VALUES(6,48,14);
INSERT INTO BingoTicket_Track VALUES(7,2,0);
INSERT INTO BingoTicket_Track VALUES(7,5,1);
INSERT INTO BingoTicket_Track VALUES(7,9,2);
INSERT INTO BingoTicket_Track VALUES(7,14,3);
INSERT INTO BingoTicket_Track VALUES(7,15,4);
INSERT INTO BingoTicket_Track VALUES(7,17,5);
INSERT INTO BingoTicket_Track VALUES(7,19,6);
INSERT INTO BingoTicket_Track VALUES(7,23,7);
INSERT INTO BingoTicket_Track VALUES(7,24,8);
INSERT INTO BingoTicket_Track VALUES(7,28,9);
INSERT INTO BingoTicket_Track VALUES(7,34,10);
INSERT INTO BingoTicket_Track VALUES(7,36,11);
INSERT INTO BingoTicket_Track VALUES(7,38,12);
INSERT INTO BingoTicket_Track VALUES(7,41,13);
INSERT INTO BingoTicket_Track VALUES(7,45,14);
INSERT INTO BingoTicket_Track VALUES(8,7,0);
INSERT INTO BingoTicket_Track VALUES(8,10,1);
INSERT INTO BingoTicket_Track VALUES(8,12,2);
INSERT INTO BingoTicket_Track VALUES(8,17,3);
INSERT INTO BingoTicket_Track VALUES(8,24,4);
INSERT INTO BingoTicket_Track VALUES(8,25,5);
INSERT INTO BingoTicket_Track VALUES(8,28,6);
INSERT INTO BingoTicket_Track VALUES(8,30,7);
INSERT INTO BingoTicket_Track VALUES(8,31,8);
INSERT INTO BingoTicket_Track VALUES(8,35,9);
INSERT INTO BingoTicket_Track VALUES(8,37,10);
INSERT INTO BingoTicket_Track VALUES(8,38,11);
INSERT INTO BingoTicket_Track VALUES(8,40,12);
INSERT INTO BingoTicket_Track VALUES(8,41,13);
INSERT INTO BingoTicket_Track VALUES(8,49,14);
INSERT INTO BingoTicket_Track VALUES(9,4,0);
INSERT INTO BingoTicket_Track VALUES(9,7,1);
INSERT INTO BingoTicket_Track VALUES(9,10,2);
INSERT INTO BingoTicket_Track VALUES(9,11,3);
INSERT INTO BingoTicket_Track VALUES(9,15,4);
INSERT INTO BingoTicket_Track VALUES(9,16,5);
INSERT INTO BingoTicket_Track VALUES(9,21,6);
INSERT INTO BingoTicket_Track VALUES(9,22,7);
INSERT INTO BingoTicket_Track VALUES(9,33,8);
INSERT INTO BingoTicket_Track VALUES(9,36,9);
INSERT INTO BingoTicket_Track VALUES(9,39,10);
INSERT INTO BingoTicket_Track VALUES(9,40,11);
INSERT INTO BingoTicket_Track VALUES(9,41,12);
INSERT INTO BingoTicket_Track VALUES(9,42,13);
INSERT INTO BingoTicket_Track VALUES(9,44,14);
INSERT INTO BingoTicket_Track VALUES(10,3,0);
INSERT INTO BingoTicket_Track VALUES(10,14,1);
INSERT INTO BingoTicket_Track VALUES(10,19,2);
INSERT INTO BingoTicket_Track VALUES(10,22,3);
INSERT INTO BingoTicket_Track VALUES(10,23,4);
INSERT INTO BingoTicket_Track VALUES(10,24,5);
INSERT INTO BingoTicket_Track VALUES(10,25,6);
INSERT INTO BingoTicket_Track VALUES(10,28,7);
INSERT INTO BingoTicket_Track VALUES(10,35,8);
INSERT INTO BingoTicket_Track VALUES(10,37,9);
INSERT INTO BingoTicket_Track VALUES(10,39,10);
INSERT INTO BingoTicket_Track VALUES(10,40,11);
INSERT INTO BingoTicket_Track VALUES(10,41,12);
INSERT INTO BingoTicket_Track VALUES(10,49,13);
INSERT INTO BingoTicket_Track VALUES(10,50,14);
INSERT INTO BingoTicket_Track VALUES(11,6,0);
INSERT INTO BingoTicket_Track VALUES(11,10,1);
INSERT INTO BingoTicket_Track VALUES(11,14,2);
INSERT INTO BingoTicket_Track VALUES(11,19,3);
INSERT INTO BingoTicket_Track VALUES(11,21,4);
INSERT INTO BingoTicket_Track VALUES(11,23,5);
INSERT INTO BingoTicket_Track VALUES(11,24,6);
INSERT INTO BingoTicket_Track VALUES(11,25,7);
INSERT INTO BingoTicket_Track VALUES(11,29,8);
INSERT INTO BingoTicket_Track VALUES(11,32,9);
INSERT INTO BingoTicket_Track VALUES(11,35,10);
INSERT INTO BingoTicket_Track VALUES(11,39,11);
INSERT INTO BingoTicket_Track VALUES(11,40,12);
INSERT INTO BingoTicket_Track VALUES(11,49,13);
INSERT INTO BingoTicket_Track VALUES(11,50,14);
INSERT INTO BingoTicket_Track VALUES(12,2,0);
INSERT INTO BingoTicket_Track VALUES(12,3,1);
INSERT INTO BingoTicket_Track VALUES(12,5,2);
INSERT INTO BingoTicket_Track VALUES(12,8,3);
INSERT INTO BingoTicket_Track VALUES(12,9,4);
INSERT INTO BingoTicket_Track VALUES(12,10,5);
INSERT INTO BingoTicket_Track VALUES(12,11,6);
INSERT INTO BingoTicket_Track VALUES(12,15,7);
INSERT INTO BingoTicket_Track VALUES(12,23,8);
INSERT INTO BingoTicket_Track VALUES(12,27,9);
INSERT INTO BingoTicket_Track VALUES(12,32,10);
INSERT INTO BingoTicket_Track VALUES(12,39,11);
INSERT INTO BingoTicket_Track VALUES(12,45,12);
INSERT INTO BingoTicket_Track VALUES(12,48,13);
INSERT INTO BingoTicket_Track VALUES(12,49,14);
INSERT INTO BingoTicket_Track VALUES(13,5,0);
INSERT INTO BingoTicket_Track VALUES(13,7,1);
INSERT INTO BingoTicket_Track VALUES(13,8,2);
INSERT INTO BingoTicket_Track VALUES(13,11,3);
INSERT INTO BingoTicket_Track VALUES(13,14,4);
INSERT INTO BingoTicket_Track VALUES(13,20,5);
INSERT INTO BingoTicket_Track VALUES(13,21,6);
INSERT INTO BingoTicket_Track VALUES(13,22,7);
INSERT INTO BingoTicket_Track VALUES(13,23,8);
INSERT INTO BingoTicket_Track VALUES(13,31,9);
INSERT INTO BingoTicket_Track VALUES(13,33,10);
INSERT INTO BingoTicket_Track VALUES(13,36,11);
INSERT INTO BingoTicket_Track VALUES(13,41,12);
INSERT INTO BingoTicket_Track VALUES(13,43,13);
INSERT INTO BingoTicket_Track VALUES(13,49,14);
INSERT INTO BingoTicket_Track VALUES(14,3,0);
INSERT INTO BingoTicket_Track VALUES(14,12,1);
INSERT INTO BingoTicket_Track VALUES(14,14,2);
INSERT INTO BingoTicket_Track VALUES(14,17,3);
INSERT INTO BingoTicket_Track VALUES(14,18,4);
INSERT INTO BingoTicket_Track VALUES(14,19,5);
INSERT INTO BingoTicket_Track VALUES(14,27,6);
INSERT INTO BingoTicket_Track VALUES(14,28,7);
INSERT INTO BingoTicket_Track VALUES(14,31,8);
INSERT INTO BingoTicket_Track VALUES(14,32,9);
INSERT INTO BingoTicket_Track VALUES(14,36,10);
INSERT INTO BingoTicket_Track VALUES(14,39,11);
INSERT INTO BingoTicket_Track VALUES(14,42,12);
INSERT INTO BingoTicket_Track VALUES(14,43,13);
INSERT INTO BingoTicket_Track VALUES(14,47,14);
INSERT INTO BingoTicket_Track VALUES(15,1,0);
INSERT INTO BingoTicket_Track VALUES(15,6,1);
INSERT INTO BingoTicket_Track VALUES(15,10,2);
INSERT INTO BingoTicket_Track VALUES(15,14,3);
INSERT INTO BingoTicket_Track VALUES(15,17,4);
INSERT INTO BingoTicket_Track VALUES(15,22,5);
INSERT INTO BingoTicket_Track VALUES(15,23,6);
INSERT INTO BingoTicket_Track VALUES(15,25,7);
INSERT INTO BingoTicket_Track VALUES(15,30,8);
INSERT INTO BingoTicket_Track VALUES(15,36,9);
INSERT INTO BingoTicket_Track VALUES(15,37,10);
INSERT INTO BingoTicket_Track VALUES(15,39,11);
INSERT INTO BingoTicket_Track VALUES(15,43,12);
INSERT INTO BingoTicket_Track VALUES(15,46,13);
INSERT INTO BingoTicket_Track VALUES(15,50,14);
INSERT INTO BingoTicket_Track VALUES(16,1,0);
INSERT INTO BingoTicket_Track VALUES(16,3,1);
INSERT INTO BingoTicket_Track VALUES(16,5,2);
INSERT INTO BingoTicket_Track VALUES(16,7,3);
INSERT INTO BingoTicket_Track VALUES(16,9,4);
INSERT INTO BingoTicket_Track VALUES(16,15,5);
INSERT INTO BingoTicket_Track VALUES(16,24,6);
INSERT INTO BingoTicket_Track VALUES(16,25,7);
INSERT INTO BingoTicket_Track VALUES(16,32,8);
INSERT INTO BingoTicket_Track VALUES(16,35,9);
INSERT INTO BingoTicket_Track VALUES(16,38,10);
INSERT INTO BingoTicket_Track VALUES(16,46,11);
INSERT INTO BingoTicket_Track VALUES(16,48,12);
INSERT INTO BingoTicket_Track VALUES(16,49,13);
INSERT INTO BingoTicket_Track VALUES(16,50,14);
INSERT INTO BingoTicket_Track VALUES(17,5,0);
INSERT INTO BingoTicket_Track VALUES(17,7,1);
INSERT INTO BingoTicket_Track VALUES(17,10,2);
INSERT INTO BingoTicket_Track VALUES(17,15,3);
INSERT INTO BingoTicket_Track VALUES(17,16,4);
INSERT INTO BingoTicket_Track VALUES(17,17,5);
INSERT INTO BingoTicket_Track VALUES(17,18,6);
INSERT INTO BingoTicket_Track VALUES(17,20,7);
INSERT INTO BingoTicket_Track VALUES(17,23,8);
INSERT INTO BingoTicket_Track VALUES(17,31,9);
INSERT INTO BingoTicket_Track VALUES(17,32,10);
INSERT INTO BingoTicket_Track VALUES(17,38,11);
INSERT INTO BingoTicket_Track VALUES(17,39,12);
INSERT INTO BingoTicket_Track VALUES(17,40,13);
INSERT INTO BingoTicket_Track VALUES(17,50,14);
INSERT INTO BingoTicket_Track VALUES(18,4,0);
INSERT INTO BingoTicket_Track VALUES(18,5,1);
INSERT INTO BingoTicket_Track VALUES(18,7,2);
INSERT INTO BingoTicket_Track VALUES(18,8,3);
INSERT INTO BingoTicket_Track VALUES(18,11,4);
INSERT INTO BingoTicket_Track VALUES(18,13,5);
INSERT INTO BingoTicket_Track VALUES(18,21,6);
INSERT INTO BingoTicket_Track VALUES(18,25,7);
INSERT INTO BingoTicket_Track VALUES(18,27,8);
INSERT INTO BingoTicket_Track VALUES(18,34,9);
INSERT INTO BingoTicket_Track VALUES(18,37,10);
INSERT INTO BingoTicket_Track VALUES(18,41,11);
INSERT INTO BingoTicket_Track VALUES(18,43,12);
INSERT INTO BingoTicket_Track VALUES(18,49,13);
INSERT INTO BingoTicket_Track VALUES(18,50,14);
INSERT INTO BingoTicket_Track VALUES(19,1,0);
INSERT INTO BingoTicket_Track VALUES(19,4,1);
INSERT INTO BingoTicket_Track VALUES(19,9,2);
INSERT INTO BingoTicket_Track VALUES(19,13,3);
INSERT INTO BingoTicket_Track VALUES(19,14,4);
INSERT INTO BingoTicket_Track VALUES(19,18,5);
INSERT INTO BingoTicket_Track VALUES(19,20,6);
INSERT INTO BingoTicket_Track VALUES(19,21,7);
INSERT INTO BingoTicket_Track VALUES(19,25,8);
INSERT INTO BingoTicket_Track VALUES(19,27,9);
INSERT INTO BingoTicket_Track VALUES(19,32,10);
INSERT INTO BingoTicket_Track VALUES(19,37,11);
INSERT INTO BingoTicket_Track VALUES(19,38,12);
INSERT INTO BingoTicket_Track VALUES(19,43,13);
INSERT INTO BingoTicket_Track VALUES(19,46,14);
INSERT INTO BingoTicket_Track VALUES(20,7,0);
INSERT INTO BingoTicket_Track VALUES(20,10,1);
INSERT INTO BingoTicket_Track VALUES(20,11,2);
INSERT INTO BingoTicket_Track VALUES(20,17,3);
INSERT INTO BingoTicket_Track VALUES(20,20,4);
INSERT INTO BingoTicket_Track VALUES(20,27,5);
INSERT INTO BingoTicket_Track VALUES(20,29,6);
INSERT INTO BingoTicket_Track VALUES(20,30,7);
INSERT INTO BingoTicket_Track VALUES(20,33,8);
INSERT INTO BingoTicket_Track VALUES(20,37,9);
INSERT INTO BingoTicket_Track VALUES(20,39,10);
INSERT INTO BingoTicket_Track VALUES(20,40,11);
INSERT INTO BingoTicket_Track VALUES(20,46,12);
INSERT INTO BingoTicket_Track VALUES(20,48,13);
INSERT INTO BingoTicket_Track VALUES(20,50,14);
INSERT INTO BingoTicket_Track VALUES(21,9,0);
INSERT INTO BingoTicket_Track VALUES(21,12,1);
INSERT INTO BingoTicket_Track VALUES(21,16,2);
INSERT INTO BingoTicket_Track VALUES(21,17,3);
INSERT INTO BingoTicket_Track VALUES(21,19,4);
INSERT INTO BingoTicket_Track VALUES(21,22,5);
INSERT INTO BingoTicket_Track VALUES(21,23,6);
INSERT INTO BingoTicket_Track VALUES(21,26,7);
INSERT INTO BingoTicket_Track VALUES(21,30,8);
INSERT INTO BingoTicket_Track VALUES(21,34,9);
INSERT INTO BingoTicket_Track VALUES(21,37,10);
INSERT INTO BingoTicket_Track VALUES(21,44,11);
INSERT INTO BingoTicket_Track VALUES(21,45,12);
INSERT INTO BingoTicket_Track VALUES(21,48,13);
INSERT INTO BingoTicket_Track VALUES(21,50,14);
INSERT INTO BingoTicket_Track VALUES(22,1,0);
INSERT INTO BingoTicket_Track VALUES(22,6,1);
INSERT INTO BingoTicket_Track VALUES(22,10,2);
INSERT INTO BingoTicket_Track VALUES(22,11,3);
INSERT INTO BingoTicket_Track VALUES(22,14,4);
INSERT INTO BingoTicket_Track VALUES(22,19,5);
INSERT INTO BingoTicket_Track VALUES(22,26,6);
INSERT INTO BingoTicket_Track VALUES(22,28,7);
INSERT INTO BingoTicket_Track VALUES(22,35,8);
INSERT INTO BingoTicket_Track VALUES(22,36,9);
INSERT INTO BingoTicket_Track VALUES(22,38,10);
INSERT INTO BingoTicket_Track VALUES(22,41,11);
INSERT INTO BingoTicket_Track VALUES(22,42,12);
INSERT INTO BingoTicket_Track VALUES(22,43,13);
INSERT INTO BingoTicket_Track VALUES(22,49,14);
INSERT INTO BingoTicket_Track VALUES(23,1,0);
INSERT INTO BingoTicket_Track VALUES(23,2,1);
INSERT INTO BingoTicket_Track VALUES(23,14,2);
INSERT INTO BingoTicket_Track VALUES(23,15,3);
INSERT INTO BingoTicket_Track VALUES(23,20,4);
INSERT INTO BingoTicket_Track VALUES(23,22,5);
INSERT INTO BingoTicket_Track VALUES(23,24,6);
INSERT INTO BingoTicket_Track VALUES(23,25,7);
INSERT INTO BingoTicket_Track VALUES(23,28,8);
INSERT INTO BingoTicket_Track VALUES(23,29,9);
INSERT INTO BingoTicket_Track VALUES(23,35,10);
INSERT INTO BingoTicket_Track VALUES(23,40,11);
INSERT INTO BingoTicket_Track VALUES(23,43,12);
INSERT INTO BingoTicket_Track VALUES(23,44,13);
INSERT INTO BingoTicket_Track VALUES(23,50,14);
INSERT INTO BingoTicket_Track VALUES(24,7,0);
INSERT INTO BingoTicket_Track VALUES(24,12,1);
INSERT INTO BingoTicket_Track VALUES(24,18,2);
INSERT INTO BingoTicket_Track VALUES(24,22,3);
INSERT INTO BingoTicket_Track VALUES(24,24,4);
INSERT INTO BingoTicket_Track VALUES(24,25,5);
INSERT INTO BingoTicket_Track VALUES(24,27,6);
INSERT INTO BingoTicket_Track VALUES(24,31,7);
INSERT INTO BingoTicket_Track VALUES(24,32,8);
INSERT INTO BingoTicket_Track VALUES(24,34,9);
INSERT INTO BingoTicket_Track VALUES(24,35,10);
INSERT INTO BingoTicket_Track VALUES(24,40,11);
INSERT INTO BingoTicket_Track VALUES(24,42,12);
INSERT INTO BingoTicket_Track VALUES(24,43,13);
INSERT INTO BingoTicket_Track VALUES(24,49,14);
CREATE UNIQUE INDEX "ix_Directory_name" ON "Directory" (name);
CREATE UNIQUE INDEX "ix_Artist_name" ON "Artist" (name);
CREATE INDEX "ix_Song_title" ON "Song" (title);
CREATE INDEX "ix_Song_filename" ON "Song" (filename);
CREATE INDEX "ix_Song_album" ON "Song" (album);
CREATE INDEX "ix_Song_uuid" ON "Song" (uuid);
COMMIT;
