"""Out-of-sample check: model fitted on matchdays 1-4 vs bookmaker odds for matchday 5."""
import math, sys
import numpy as np
import market_data as M, upcoming_odds as U, ucl_sim as S

rng = np.random.default_rng(3); Z = rng.standard_normal((40000, 2))

def new_model(hp, ap):
    up = S.UPPER_PER_POT / S.TEAMS_PER_POT; out = np.zeros(3)
    for th, wh in (((hp-1)*2, up), ((hp-1)*2+1, 1-up)):
        for ta, wa in (((ap-1)*2, up), ((ap-1)*2+1, 1-up)):
            x = S.tier_strength(th)-S.tier_strength(ta)+S.HOME_ADV+S.POT_HOME_EDGE[hp-1]+S.TEAM_SD*(Z[:,0]-Z[:,1])
            tie = np.clip(S.TIE0-S.TIE_FADE*np.abs(x), S.TIE_MIN, None); win = (1-tie)/(1+np.exp(-x))
            out += wh*wa*np.array([win.mean(), tie.mean(), (1-tie-win).mean()])
    return out
def old_model(hp, ap):          # v1: equal pot steps, home 0.65, tie scale 0.5
    St=[1.65,1.10,0.55,0.0]; out=np.zeros(3)
    for th,wh in (((hp-1)*2,4/9),((hp-1)*2+1,5/9)):
        for ta,wa in (((ap-1)*2,4/9),((ap-1)*2+1,5/9)):
            ts=lambda k: St[k>>1]+(.175 if k%2==0 else -.175)
            x=ts(th)-ts(ta)+.65; t0=max(.05,.457-.1322*abs(x)); o=math.exp(x); w=(1-t0)*o/(1+o); fr=t0*.5
            out+=wh*wa*np.array([w+fr/2, t0-fr, 1-w-t0+fr/2])
    return out

ALIAS = {"Paris Saint-Germain":"Paris Saint-Germain","Roma":"Roma"}
rows = []
for h, a, oh, od, oa in U.UPCOMING:
    raw = np.array([1/oh, 1/od, 1/oa]); p = raw/raw.sum()
    rows.append(dict(h=h, a=a, ph=M.pot_of(h), pa=M.pot_of(a), p=p, margin=raw.sum()-1))
cross = [r for r in rows if r['ph'] != r['pa']]
print(f"{len(rows)} games ({len(cross)} between different pots). Average margin {100*np.mean([r['margin'] for r in rows]):.1f}%\n")
print(f"{'Match (home v away)':<36}{'pots':>5} | {'market W/D/L %':^17} | {'model W/D/L %':^17} | {'gap (pp)':^18}")
for r in cross:
    mo = new_model(r['ph'], r['pa']); m = r['p']
    print(f"{r['h']+' v '+r['a']:<36}{r['ph']}v{r['pa']:<3} | {100*m[0]:5.1f}{100*m[1]:6.1f}{100*m[2]:6.1f} | {100*mo[0]:5.1f}{100*mo[1]:6.1f}{100*mo[2]:6.1f} | {100*(mo[0]-m[0]):+5.1f}{100*(mo[1]-m[1]):+6.1f}{100*(mo[2]-m[2]):+6.1f}")
def mae(fn, rs):
    pr = np.array([fn(r['ph'], r['pa']) for r in rs]); P = np.array([r['p'] for r in rs]); return 100*np.abs(pr-P).mean(0), pr, P
for label, rs in (("different pots (15)", cross), ("all 18", rows)):
    print(f"\nMean absolute gap to market, {label}:")
    for nm, fn in (("  new model (fitted on MD1-4)", new_model), ("  old model (hand-set)", old_model)):
        e, pr, P = mae(fn, rs); print(f"{nm:<32} win {e[0]:4.1f}  draw {e[1]:4.1f}  loss {e[2]:4.1f} pp   avg draw: model {100*pr[:,1].mean():.1f}% vs market {100*P[:,1].mean():.1f}%")
# stronger-side view
print("\nBy pot pairing (stronger pot's win chance), market vs new model:")
import collections; g = collections.defaultdict(list)
for r in cross:
    fav_home = r['ph'] < r['pa']; mo = new_model(r['ph'], r['pa']); i = 0 if fav_home else 2
    g[(min(r['ph'],r['pa']), max(r['ph'],r['pa']), 'home' if fav_home else 'away')].append((r['p'][i], mo[i]))
for k in sorted(g):
    v = g[k]; print(f"  pot {k[0]} {k[2]:<4} v pot {k[1]}: n={len(v)}  market {100*np.mean([x[0] for x in v]):.0f}%  model {100*np.mean([x[1] for x in v]):.0f}%")

# does the fit change if we add these 18 games? (refit on all 75, same method as fit_market.py)
def fit(rs):
    ph = [r['ph'] for r in rs]; pa = [r['pa'] for r in rs]
    A = np.zeros((len(rs), 4))
    for i,(h,a) in enumerate(zip(ph,pa)):
        if h<4: A[i,h-1]+=1
        if a<4: A[i,a-1]-=1
        A[i,3]=1
    X = np.array([math.log(r['p'][0]/r['p'][2]) for r in rs]); D = np.array([r['p'][1] for r in rs])
    b,*_ = np.linalg.lstsq(A, X, rcond=None); res = X-A@b; sw = math.sqrt(res@res/(len(rs)-4))/math.sqrt(2)
    B = np.vstack([np.ones(len(rs)), -np.abs(X)]).T; c,*_ = np.linalg.lstsq(B, D, rcond=None)
    return b, sw, c
old_rows = M.dataset()
for nm, rs in (("MD1-4 (57 games)", old_rows), ("MD5 alone (18)", rows), ("all 75 games", old_rows + rows)):
    b, sw, c = fit(rs)
    print(f"fit on {nm:<18}: pot strengths {b[0]:.2f}, {b[1]:.2f}, {b[2]:.2f}, 0 | home {b[3]:.2f} | within-pot SD {sw:.2f} | draw {c[0]:.3f} - {c[1]:.3f}|x|")
