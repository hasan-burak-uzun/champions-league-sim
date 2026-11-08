import math, numpy as np
import uel_data as U
R=U.dataset(); n=len(R)
X=np.array([math.log(r['p'][0]/r['p'][2]) for r in R]); D=np.array([r['p'][1] for r in R])
A=np.zeros((n,4))
for i,r in enumerate(R):
    if r['ph']<4:A[i,r['ph']-1]+=1
    if r['pa']<4:A[i,r['pa']-1]-=1
    A[i,3]=1
b,*_=np.linalg.lstsq(A,X,rcond=None); res=X-A@b; s=math.sqrt(res@res/(n-4)); se=np.sqrt(np.diag(s*s*np.linalg.inv(A.T@A)))
print(n,"games"); [print(f"  {nm:8}{v:6.3f} +/- {e:.3f}") for nm,v,e in zip(["S1","S2","S3","H"],b,se)]
print(f"  resid SD {s:.3f} -> within-pot team SD {s/math.sqrt(2):.3f}")
ax=np.abs(X); B=np.vstack([np.ones(n),-ax]).T; c,*_=np.linalg.lstsq(B,D,rcond=None)
print(f"  draw {c[0]:.3f} - {c[1]:.3f}|x|; mean draw {D.mean():.3f}; resid SD {(D-B@c).std():.3f}")
# 3-parameter alt: equal spacing S1=2d,S2=d... S3 fixed by linear (S_k=(4-k)*d)
A2=np.zeros((n,2))
for i,r in enumerate(R):
    A2[i,0]=(4-r['ph'])-(4-r['pa']); A2[i,1]=1
b2,*_=np.linalg.lstsq(A2,X,rcond=None); r2=X-A2@b2; s2=math.sqrt(r2@r2/(n-2))
print(f"linear-spacing fit: step {b2[0]:.3f}, H {b2[1]:.3f}, resid SD {s2:.3f}  -> S1..S3 = {3*b2[0]:.2f},{2*b2[0]:.2f},{b2[0]:.2f}")
for r,x in zip(R,X): print(f"  MD{r['md']} {r['h']:11}({r['ph']}) v {r['a']:11}({r['pa']}) mkt {r['p'][0]:.2f}/{r['p'][1]:.2f}/{r['p'][2]:.2f}")
