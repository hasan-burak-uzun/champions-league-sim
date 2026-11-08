import math, sys, numpy as np
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_data as M
rows = M.dataset()
n = len(rows)
X = np.array([[math.log(r['p'][0]/r['p'][2])] for r in rows]).ravel()   # market ln(win/loss) for home team
D = np.array([r['p'][1] for r in rows])
ph = np.array([r['ph'] for r in rows]); pa = np.array([r['pa'] for r in rows])
md = np.array([r['md'] for r in rows])

def design(ph, pa):
    A = np.zeros((len(ph), 4))   # columns: S1, S2, S3, H   (S4 = 0)
    for i, (h, a) in enumerate(zip(ph, pa)):
        if h < 4: A[i, h-1] += 1
        if a < 4: A[i, a-1] -= 1
        A[i, 3] = 1
    return A
A = design(ph, pa)
beta, *_ = np.linalg.lstsq(A, X, rcond=None)
res = X - A @ beta
dof = n - 4
s = math.sqrt(res @ res / dof)
cov = s**2 * np.linalg.inv(A.T @ A)
se = np.sqrt(np.diag(cov))
names = ["S1 (pot 1)","S2 (pot 2)","S3 (pot 3)","Home adv"]
print(f"{n} games. OLS on market ln(home win / away win)")
for nm, b, e in zip(names, beta, se): print(f"  {nm:<12}{b:6.3f}  +/- {e:.3f}")
print(f"  residual SD {s:.3f}  -> implied SD of a team's strength within its pot ~ {s/math.sqrt(2):.3f}")
print("  steps between pots:", f"1->2 {beta[0]-beta[1]:.2f}, 2->3 {beta[1]-beta[2]:.2f}, 3->4 {beta[2]:.2f}")

# heteroscedasticity: does the residual spread depend on whether pot 1 is involved?
inv1 = (ph == 1) | (pa == 1)
print(f"  resid SD with pot 1 involved {res[inv1].std(ddof=0):.3f} (n={inv1.sum()}), without {res[~inv1].std(ddof=0):.3f} (n={(~inv1).sum()})")
for k in (1,2,3,4):
    m = md == k; print(f"  matchday {k}: mean residual {res[m].mean():+.3f}, SD {res[m].std():.3f} (n={m.sum()})")
# per-pot home advantage
Ah = np.hstack([A[:, :3], np.array([[1.0 if h == p else 0.0 for p in (1,2,3,4)] for h in ph])])
b2, *_ = np.linalg.lstsq(Ah, X, rcond=None); r2 = X - Ah @ b2
print("  home advantage by home pot (free fit):", np.round(b2[3:], 2), " (n by pot:", [int((ph==p).sum()) for p in (1,2,3,4)], ")")
print(f"  residual SD with per-pot home adv {math.sqrt(r2@r2/(n-7)):.3f} vs {s:.3f}")

# draw curve: draw prob vs |x|
ax = np.abs(X)
Bd = np.vstack([np.ones(n), -ax]).T
cd, *_ = np.linalg.lstsq(Bd, D, rcond=None); rd = D - Bd @ cd
print(f"\nDraw curve: P(draw) = {cd[0]:.3f} - {cd[1]:.3f}*|x|   resid SD {rd.std():.3f}; mean market draw {D.mean():.3f}")
for lo, hi in [(0,.3),(.3,.7),(.7,1.2),(1.2,2),(2,5)]:
    m = (ax >= lo) & (ax < hi); print(f"   |x| in [{lo},{hi}): n={m.sum():2d} market draw {D[m].mean():.3f}  fitted {np.mean(cd[0]-cd[1]*ax[m]):.3f}")
# quadratic check
Bq = np.vstack([np.ones(n), -ax, ax**2]).T; cq, *_ = np.linalg.lstsq(Bq, D, rcond=None)
print(f"   quadratic alt: {cq[0]:.3f} - {cq[1]:.3f}|x| + {cq[2]:.3f}x^2  resid SD {(D-Bq@cq).std():.3f}")
