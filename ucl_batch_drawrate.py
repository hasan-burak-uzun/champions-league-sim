"""
Run the batch with the draw chance calibrated to an observed average draw rate.
Usage: python3 ucl_batch_drawrate.py DRAWS GAMES [n_sims] [seed]
e.g.   python3 ucl_batch_drawrate.py 7 72      (2026-27 UCL after 4 matchdays: 9.7% drawn)
Only the draw chance in an even match (TIE0) is changed; the fade with lopsidedness stays at TIE_FADE.
"""
import random
import sys

import ucl_sim as S
import ucl_batch as B


def avg_draw(tie0, seasons=60, seed=11):
    """Average draw share of a match, including the per-team random strength."""
    rng = random.Random(seed)
    tot = n = 0
    for _ in range(seasons):
        games = S.build_fixtures(rng)
        st = [S.tier_strength(S.tier_of(t)) + o for t, o in enumerate(S.draw_team_offsets(rng))]
        for h, a in games:
            x = st[h] - st[a] + S.HOME_ADV + S.POT_HOME_EDGE[S.pot_of(h)]
            tot += S.probs_from_x(x, tie0)[1]
            n += 1
    return tot / n


def calibrate(target):
    lo, hi = 0.0, 0.6
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if avg_draw(mid) < target else (lo, mid)
    return (lo + hi) / 2


if __name__ == "__main__":
    draws, games = int(sys.argv[1]), int(sys.argv[2])
    target = draws / games
    S.TIE0 = calibrate(target)
    print(f"Observed draw rate {draws}/{games} = {target:.1%} -> TIE0 = {S.TIE0:.3f}\n")
    B.BASE_TIE = S.TIE0
    sys.argv = [sys.argv[0]] + sys.argv[3:]
    B.main()
