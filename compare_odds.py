"""
Compare bookmaker 1X2 odds (2026-27 Champions League, matchdays 1-4, 57 games) with the simulator's odds.
Odds: American format from DraftKings / FanDuel / BetRivers / LetsBetMD (rg.org); margin removed per book, averaged.
Model: ucl_sim v2 defaults, averaged over each pot's two groups and over the random team strengths.
Usage: python3 compare_odds.py
"""
import collections
import math
import random

import numpy as np

import market_data as M
import ucl_sim as S

rows = M.dataset()
rng = np.random.default_rng(3)
Z = rng.standard_normal((40000, 2))


def model(hp, ap):
    """Expected (home win, draw, away win) for a pot pairing under ucl_sim's current parameters."""
    up = S.UPPER_PER_POT / S.TEAMS_PER_POT
    out = np.zeros(3)
    for th, wh in (((hp - 1) * 2, up), ((hp - 1) * 2 + 1, 1 - up)):
        for ta, wa in (((ap - 1) * 2, up), ((ap - 1) * 2 + 1, 1 - up)):
            x = (S.tier_strength(th) - S.tier_strength(ta) + S.HOME_ADV + S.POT_HOME_EDGE[hp - 1]
                 + S.TEAM_SD * (Z[:, 0] - Z[:, 1]))
            tie = np.clip(S.TIE0 - S.TIE_FADE * np.abs(x), S.TIE_MIN, None)
            win = (1 - tie) / (1 + np.exp(-x))
            out += wh * wa * np.array([win.mean(), tie.mean(), (1 - tie - win).mean()])
    return out


by = collections.defaultdict(list)
for r in rows:
    by[(r["ph"], r["pa"])].append(r["p"])

print(f"{len(rows)} games ({sum(r['ph'] != r['pa'] for r in rows)} between different pots). "
      f"Average bookmaker margin {100 * np.mean([r['margin'] for r in rows]):.1f}%\n")
print(f"{'home pot v away pot':<20}{'n':>3} | {'market W/D/L %':^17} | {'model W/D/L %':^17} | {'gap W/D/L (pp)':^18}")
ae = np.zeros(3)
for k in sorted(by):
    m = 100 * np.mean(by[k], axis=0)
    mo = 100 * model(*k)
    ae += len(by[k]) * np.abs(mo - m)
    print(f"  pot {k[0]} v pot {k[1]:<8}{len(by[k]):>3} | {m[0]:5.1f}{m[1]:6.1f}{m[2]:6.1f} | {mo[0]:5.1f}{mo[1]:6.1f}{mo[2]:6.1f} | "
          f"{mo[0]-m[0]:+5.1f}{mo[1]-m[1]:+6.1f}{mo[2]-m[2]:+6.1f}")
ae /= len(rows)
print(f"\nmean absolute gap by pairing, weighted by games (pp): win {ae[0]:.1f}, draw {ae[1]:.1f}, loss {ae[2]:.1f}")
print(f"average draw share: market {100 * np.mean([r['p'][1] for r in rows]):.1f}%")
