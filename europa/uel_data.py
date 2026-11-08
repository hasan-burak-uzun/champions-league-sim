"""Europa League 2026-27 league phase: bookmaker odds (MD3 + MD4), pots from UEFA. Source: rg.org (Oct 20 & Nov 3 2026)."""
import math
POT = {"Leverkusen":1,"Marseille":1,"Milan":1,"Ferencvaros":2,"AZ":1,"Juventus":1,"Palace":3,"Hoffenheim":4,
       "Celtic":2,"Besiktas":4,"Sunderland":3,"Dinamo":2,"Bournemouth":3,"Rennes":2,"Lyon":1,"Celta":3,
       "Lech":3,"Sturm":3}
def us(o): return 1+o/100 if o>0 else 1+100/-o
# (matchday, home, away, [books]) each book = (home, draw, away) in decimal
G=[]
def am(md,h,a,*bk): G.append((md,h,a,[tuple(us(x) for x in b) for b in bk]))
def dc(md,h,a,*bk): G.append((md,h,a,[tuple(b) for b in bk]))
# MD4 (American, FanDuel/DraftKings/BetRivers/LetsBetMD)
am(4,"Leverkusen","Marseille",(-278,400,550),(-244,425,550),(-250,370,540),(-250,380,600))
am(4,"Milan","Ferencvaros",(-417,490,750),(-323,475,800),(-357,425,750),(-357,440,825))
am(4,"AZ","Juventus",(260,260,-105),(275,280,-105),(260,245,-110),(270,265,-114))
am(4,"Palace","Hoffenheim",(-105,280,250),(-105,295,250),(-108,270,230),(-111,295,245))
am(4,"Celtic","Besiktas",(210,290,105),(210,285,115),(200,260,108),(200,285,110))
am(4,"Sunderland","Dinamo",(-250,370,550),(-208,370,550),(-233,335,540),(-238,335,600))
# MD3 (decimal: 1xBet, Tonybet, 22Bet, 20Bet, Granawin; BetLabel = 22Bet duplicate, dropped)
dc(3,"Juventus","Rennes",(1.61,4.31,5.58),(1.57,4.20,5.40),(1.58,4.22,5.45),(1.57,4.20,5.40),(1.57,4.20,5.40))
dc(3,"Bournemouth","Milan",(2.25,3.63,3.21),(2.20,3.65,3.05),(2.21,3.54,3.14),(2.20,3.65,3.05),(2.20,3.65,3.05))
dc(3,"Besiktas","Palace",(2.15,3.81,3.29),(2.13,3.70,3.10),(2.11,3.72,3.20),(2.13,3.70,3.10),(2.13,3.70,3.10))
dc(3,"Celtic","Celta",(2.75,3.54,2.60),(2.60,3.50,2.60),(2.69,3.46,2.54),(2.60,3.50,2.60),(2.60,3.50,2.60))
dc(3,"Hoffenheim","Lyon",(2.07,3.98,3.37),(2.04,3.85,3.25),(2.03,3.88,3.30),(2.04,3.85,3.25),(2.04,3.85,3.25))
dc(3,"Lech","Sunderland",(4.92,4.21,1.69),(5.00,3.90,1.66),(4.80,4.12,1.66),(5.00,3.90,1.66),(5.00,3.90,1.66))
dc(3,"Sturm","Marseille",(3.60,3.73,2.06),(3.40,3.55,2.07),(3.52,3.64,2.02),(3.40,3.55,2.07),(3.40,3.55,2.07))
def fair(b):
    ps=[tuple(1/x for x in o) for o in b]
    ps=[tuple(p/sum(q) for p in q) for q in ps]
    return tuple(sum(q[i] for q in ps)/len(ps) for i in range(3))
def dataset():
    return [dict(md=m,h=h,a=a,ph=POT[h],pa=POT[a],p=fair(b)) for m,h,a,b in G]
