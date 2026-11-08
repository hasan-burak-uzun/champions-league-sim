"""
Bookmaker 1X2 odds (American) for the 2026-27 Champions League league phase, matchdays 1-4.
Source: rg.org odds articles (DraftKings / FanDuel / BetRivers / LetsBetMD). Pots from SI's draw article.
 MD1: 18 games, 3 books (FD, BR, LB), prices of 6 Sep.     MD2: 6 headline games, 4 books, 12 Oct.
 MD3: 18 games, BEST price per outcome across books (one pseudo-book, noisier), 18 Oct.
 MD4: 15 games, 4 books, 1 Nov (the 3 missing games are same-pot).
"""
POT = {
 1:"Paris Saint-Germain,Bayern Munich,Real Madrid,Liverpool,Inter,Manchester City,Arsenal,Barcelona,Atletico Madrid",
 2:"Borussia Dortmund,Roma,Sporting CP,Aston Villa,Porto,Manchester United,Club Brugge,Real Betis,PSV Eindhoven",
 3:"Feyenoord,Lille,Bodo/Glimt,Napoli,RB Leipzig,Villarreal,Fenerbahce,Shakhtar Donetsk,Galatasaray",
 4:"Slavia Prague,Slovan Bratislava,Stuttgart,AEK Athens,LASK,Como,Lens,Viking,Sabah"}
POT_OF = {t: p for p, s in POT.items() for t in s.split(",")}
ALIAS = {"PSG":"Paris Saint-Germain","Man City":"Manchester City","Atletico Madrid":"Atletico Madrid","PSV":"PSV Eindhoven"}
def pot_of(t): return POT_OF[ALIAS.get(t, t)]

# (matchday, home, away, [ (H,D,A) per book ])
G = []
def add(md, h, a, *books): G.append((md, h, a, list(books)))

# ---- MD1 (FD, BR, LB)
add(1,"Club Brugge","Aston Villa",(160,260,145),(180,265,140),(165,265,147))
add(1,"AEK Athens","LASK",(-150,300,350),(-132,295,335),(-143,305,365))
add(1,"Lille","Real Betis",(120,250,210),(120,250,220),(127,260,200))
add(1,"Real Madrid","Inter",(-170,320,410),(-175,330,440),(-161,330,390))
add(1,"Borussia Dortmund","Villarreal",(-145,310,320),(-134,310,325),(-130,310,310))
add(1,"Porto","Manchester City",(350,300,-150),(360,295,-141),(335,300,-133))
add(1,"Stuttgart","Viking",(-550,600,900),(-385,540,900),(-400,575,950))
add(1,"Barcelona","Feyenoord",(-1000,800,1700),(-835,900,1700),(-833,850,1750))
add(1,"PSG","Slovan Bratislava",(-2000,1400,3500),(-1667,1300,3400),(-1667,1250,3100))
add(1,"Napoli","Arsenal",(330,260,-130),(360,255,-124),(325,265,-118))
add(1,"Liverpool","Atletico Madrid",(-165,300,380),(-143,310,370),(-133,300,335))
add(1,"Sporting CP","Galatasaray",(-120,280,280),(-114,280,290),(-111,275,285))
add(1,"PSV","Shakhtar Donetsk",(-270,410,600),(-265,420,650),(-250,400,600))
add(1,"Fenerbahce","Roma",(220,240,115),(205,245,130),(180,260,137))
add(1,"Como","RB Leipzig",(-115,280,270),(-105,275,265),(-102,285,245))
add(1,"Bayern Munich","Bodo/Glimt",(-900,750,1400),(-770,850,1600),(-714,825,1450))
add(1,"Manchester United","Sabah",(-900,750,1700),(-670,750,1400),(-769,800,1650))
add(1,"Slavia Prague","Lens",(180,250,135),(175,250,150),(180,260,140))
# ---- MD2 (FD, DK, BR, LB)
add(2,"Atletico Madrid","Manchester United",(-110,300,260),(-110,300,260),(-112,300,265),(-109,305,250))
add(2,"Manchester City","PSG",(105,300,200),(120,300,195),(116,295,195),(117,305,190))
add(2,"Roma","Real Madrid",(260,290,-120),(265,310,-115),(265,310,-114),(250,315,-111))
add(2,"Arsenal","Lille",(-476,550,1300),(-417,550,1100),(-435,525,1300),(-400,500,1100))
add(2,"Galatasaray","Barcelona",(800,600,-400),(700,600,-357),(900,550,-400),(800,575,-400))
add(2,"RB Leipzig","PSV",(-141,350,300),(-130,350,285),(-127,340,280),(-130,335,285))
# ---- MD3 (best price per outcome across books -> one pseudo-book; PSG-Barca & Bayern-Arsenal have 4 books)
add(3,"Fenerbahce","Slavia Prague",(-143,320,390))
add(3,"Sabah","Borussia Dortmund",(875,500,-333))
add(3,"Roma","Slovan Bratislava",(-588,725,1450))
add(3,"Porto","PSV",(-152,350,380))
add(3,"Liverpool","Villarreal",(-200,380,510))
add(3,"Manchester City","AEK Athens",(-1250,1200,3300))
add(3,"PSG","Barcelona",(145,340,140),(140,340,135),(143,335,145),(140,350,145))
add(3,"Napoli","Bodo/Glimt",(-164,355,420))
add(3,"Stuttgart","Atletico Madrid",(220,290,114))
add(3,"Como","Manchester United",(130,275,195))
add(3,"Lille","Galatasaray",(122,270,225))
add(3,"Aston Villa","Viking",(-385,575,1000))
add(3,"Club Brugge","Lens",(110,300,225))
add(3,"Bayern Munich","Arsenal",(125,270,200),(115,270,200),(118,265,215),(115,275,205))
add(3,"Inter","Shakhtar Donetsk",(-455,600,1100))
add(3,"Real Madrid","RB Leipzig",(-345,550,850))
add(3,"Real Betis","Feyenoord",(-189,380,500))
add(3,"Sporting CP","LASK",(-370,600,1050))
# ---- MD4 (DK, FD, BR, LB)
add(4,"Galatasaray","Stuttgart",(115,320,190),(110,300,195),(118,310,185),(125,300,180))
add(4,"Shakhtar Donetsk","Sporting CP",(265,290,-105),(260,260,-105),(255,265,100),(260,290,-109))
add(4,"Atletico Madrid","Bayern Munich",(180,295,130),(180,280,125),(195,300,118),(175,300,127))
add(4,"Barcelona","Aston Villa",(-385,600,850),(-476,600,800),(-417,600,900),(-455,600,950))
add(4,"Bodo/Glimt","Lille",(-120,310,285),(-120,300,270),(-122,310,285),(-118,305,275))
add(4,"Feyenoord","Inter",(320,340,-141),(300,320,-141),(320,320,-135),(315,335,-139))
add(4,"LASK","Slovan Bratislava",(-227,400,550),(-263,380,600),(-244,410,575),(-222,390,550))
add(4,"Manchester United","Roma",(130,300,175),(130,290,170),(132,290,175),(130,285,180))
add(4,"Villarreal","PSG",(370,360,-161),(370,360,-169),(390,360,-167),(370,370,-167))
add(4,"AEK Athens","Real Madrid",(750,500,-345),(700,490,-345),(800,480,-333),(800,500,-357))
add(4,"Fenerbahce","Liverpool",(400,350,-175),(390,340,-175),(390,335,-161),(390,340,-161))
add(4,"Borussia Dortmund","Real Betis",(-141,320,330),(-149,310,320),(-141,300,360),(-133,325,310))
add(4,"RB Leipzig","Manchester City",(425,380,-189),(410,370,-196),(450,340,-182),(445,395,-200))
add(4,"Slavia Prague","Arsenal",(750,450,-312),(700,440,-333),(900,450,-333),(875,460,-333))
add(4,"Porto","Napoli",(120,265,200),(120,260,200),(118,255,220),(122,265,200))

dec = lambda a: 1 + a/100 if a > 0 else 1 + 100/(-a)
def fair(books):
    out = []
    for b in books:
        raw = [1/dec(a) for a in b]; s = sum(raw)
        out.append(([r/s for r in raw], s-1))
    p = [sum(o[0][i] for o in out)/len(out) for i in range(3)]
    return p, sum(o[1] for o in out)/len(out)

def dataset():
    rows = []
    for md, h, a, books in G:
        p, mg = fair(books)
        rows.append(dict(md=md, h=h, a=a, ph=pot_of(h), pa=pot_of(a), p=p, margin=mg))
    return rows
