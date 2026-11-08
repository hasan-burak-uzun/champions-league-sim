import math, sys, numpy as np
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_data as M
rows = M.dataset(); n = len(rows)

# actual results of those games (H/D/A), from UEFA's matchday results
OUT = {
 # MD1
 ("AEK Athens","LASK"):"H",("Club Brugge","Aston Villa"):"A",("Borussia Dortmund","Villarreal"):"H",("Porto","Manchester City"):"A",
 ("Lille","Real Betis"):"A",("Real Madrid","Inter"):"H",("Barcelona","Feyenoord"):"H",("Stuttgart","Viking"):"H",("Liverpool","Atletico Madrid"):"H",
 ("PSG","Slovan Bratislava"):"H",("Sporting CP","Galatasaray"):"H",("Napoli","Arsenal"):"A",("Fenerbahce","Roma"):"D",("PSV","Shakhtar Donetsk"):"D",
 ("Como","RB Leipzig"):"H",("Bayern Munich","Bodo/Glimt"):"H",("Manchester United","Sabah"):"H",("Slavia Prague","Lens"):"A",
 # MD2
 ("Arsenal","Lille"):"H",("Atletico Madrid","Manchester United"):"H",("Galatasaray","Barcelona"):"A",("RB Leipzig","PSV"):"H",("Roma","Real Madrid"):"A",("Manchester City","PSG"):"A",
 # MD3
 ("Fenerbahce","Slavia Prague"):"D",("Sabah","Borussia Dortmund"):"A",("Roma","Slovan Bratislava"):"H",("Porto","PSV"):"A",("Liverpool","Villarreal"):"H",
 ("Manchester City","AEK Athens"):"H",("PSG","Barcelona"):"H",("Napoli","Bodo/Glimt"):"H",("Stuttgart","Atletico Madrid"):"D",("Como","Manchester United"):"H",
 ("Lille","Galatasaray"):"A",("Aston Villa","Viking"):"H",("Club Brugge","Lens"):"H",("Bayern Munich","Arsenal"):"D",("Inter","Shakhtar Donetsk"):"H",
 ("Real Madrid","RB Leipzig"):"H",("Real Betis","Feyenoord"):"H",("Sporting CP","LASK"):"A",
 # MD4
 ("Galatasaray","Stuttgart"):"H",("Shakhtar Donetsk","Sporting CP"):"A",("Atletico Madrid","Bayern Munich"):"A",("Barcelona","Aston Villa"):"H",("Bodo/Glimt","Lille"):"D",
 ("Feyenoord","Inter"):"A",("LASK","Slovan Bratislava"):"H",("Manchester United","Roma"):"H",("Villarreal","PSG"):"A",("AEK Athens","Real Madrid"):"A",
 ("Fenerbahce","Liverpool"):"H",("Borussia Dortmund","Real Betis"):"H",("RB Leipzig","Manchester City"):"A",("Slavia Prague","Arsenal"):"A",("Porto","Napoli"):"H",
}
idx = {"H":0,"D":1,"A":2}
y = np.array([idx[OUT[(r['h'], r['a'])]] for r in rows])
print(f"outcomes matched for {len(y)} games: H {np.sum(y==0)}, D {np.sum(y==1)}, A {np.sum(y==2)}  (draw share {np.mean(y==1):.1%})")

ph = np.array([r['ph'] for r in rows]); pa = np.array([r['pa'] for r in rows]); md = np.array([r['md'] for r in rows])
P = np.array([r['p'] for r in rows]); X = np.log(P[:,0]/P[:,2]); D = P[:,1]

def design(ph, pa):
    A = np.zeros((len(ph), 4))
    for i,(h,a) in enumerate(zip(ph,pa)):
        if h<4: A[i,h-1]+=1
        if a<4: A[i,a-1]-=1
        A[i,3]=1
    return A
def fit(idx_):
    A = design(ph[idx_], pa[idx_]); b,*_ = np.linalg.lstsq(A, X[idx_], rcond=None)
    r = X[idx_]-A@b; sw = math.sqrt(r@r/(len(idx_)-4))/math.sqrt(2)
    ax = np.abs(X[idx_]); B = np.vstack([np.ones(len(idx_)), -ax]).T; c,*_ = np.linalg.lstsq(B, D[idx_], rcond=None)
    return b, sw, c
rng = np.random.default_rng(7); Z = rng.standard_normal((40000, 2))

def new_pred(h, a, b, sw, c):
    S = [b[0],b[1],b[2],0.0]
    x = S[h-1]-S[a-1]+b[3] + sw*(Z[:,0]-Z[:,1])      # team offsets; difference of two ~N(0,sw^2)
    tie = np.clip(c[0]-c[1]*np.abs(x), 0.02, None); w = (1-tie)/(1+np.exp(-x))
    return np.array([w.mean(), tie.mean(), (1-tie-w).mean()])

# OLD model (equal pot steps, tie scale 0.5), averaged over the two groups of each pot
def old_pred(h, a):
    S=[1.65,1.10,0.55,0.0]; sub=.35; H=.65; out=np.zeros(3)
    for th,wh in (((h-1)*2,4/9),((h-1)*2+1,5/9)):
        for ta,wa in (((a-1)*2,4/9),((a-1)*2+1,5/9)):
            ts=lambda k: S[k>>1]+(sub/2 if k%2==0 else -sub/2)
            x=ts(th)-ts(ta)+H; tie0=max(0.05,0.457-0.1322*abs(x)); o=math.exp(x); win=(1-tie0)*o/(1+o); fr=tie0*0.5
            out+=wh*wa*np.array([win+fr/2, tie0-fr, 1-win-tie0+fr/2])
    return out

def score(pred, label):
    mae = np.abs(pred-P).mean(axis=0)
    ll = -np.mean(np.log(np.clip(pred[np.arange(n), y],1e-9,1)))
    br = np.mean(np.sum((pred-np.eye(3)[y])**2, axis=1))
    print(f"{label:<44} MAE vs market  H {100*mae[0]:4.1f}  D {100*mae[1]:4.1f}  A {100*mae[2]:4.1f} pp | vs actual results: log-loss {ll:.3f}, Brier {br:.3f}")
    return ll, br

allidx = np.arange(n)
b, sw, c = fit(allidx)
print(f"\nfit on all: S=({b[0]:.2f},{b[1]:.2f},{b[2]:.2f},0) home {b[3]:.2f}  within-pot SD {sw:.3f}  draw = {c[0]:.3f} - {c[1]:.3f}|x|")
pm = P
score(pm, "Market (bookmaker, margin removed)")
score(np.array([old_pred(h,a) for h,a in zip(ph,pa)]), "OLD default model (pot level)")
score(np.array([new_pred(h,a,b,sw,c) for h,a in zip(ph,pa)]), "NEW fitted model, in-sample (pot level)")
# leave-one-matchday-out
cv = np.zeros((n,3))
for k in (1,2,3,4):
    tr = np.where(md!=k)[0]; te = np.where(md==k)[0]; bk, swk, ck = fit(tr)
    for i in te: cv[i] = new_pred(ph[i],pa[i],bk,swk,ck)
score(cv, "NEW fitted model, leave-one-matchday-out")
# naive baselines
base = np.tile(np.array([P[:,0].mean(),P[:,1].mean(),P[:,2].mean()]), (n,1))
score(base, "Constant (average market H/D/A for everyone)")
print("\nAverage draw: market", f"{D.mean():.3f}", " new model", f"{np.mean([new_pred(h,a,b,sw,c)[1] for h,a in zip(ph,pa)]):.3f}", " old model", f"{np.mean([old_pred(h,a)[1] for h,a in zip(ph,pa)]):.3f}", " actual", f"{np.mean(y==1):.3f}")
# bootstrap SE on parameters
bs = []
for _ in range(2000):
    ii = rng.integers(0, n, n); A = design(ph[ii], pa[ii])
    try:
        bb,*_ = np.linalg.lstsq(A, X[ii], rcond=None); bs.append(bb)
    except Exception: pass
bs = np.array(bs); print("bootstrap 90% intervals: S1", np.round(np.percentile(bs[:,0],[5,95]),2), "S2", np.round(np.percentile(bs[:,1],[5,95]),2), "S3", np.round(np.percentile(bs[:,2],[5,95]),2), "home", np.round(np.percentile(bs[:,3],[5,95]),2))
# pot-pair table: market vs new vs old, mean H/D/A
import collections
g = collections.defaultdict(list)
for i in range(n): g[(ph[i],pa[i])].append(i)
print("\nPot pair (home v away): n | market H/D/A | NEW | OLD")
for k in sorted(g):
    ii = g[k]; m = P[ii].mean(0); nn = new_pred(k[0],k[1],b,sw,c); oo = old_pred(*k)
    f = lambda v: " ".join(f"{100*x:4.0f}" for x in v)
    print(f"  {k[0]} v {k[1]}: {len(ii):2d} | {f(m)} | {f(nn)} | {f(oo)}")
