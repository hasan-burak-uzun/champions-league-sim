"""
Run the 1,000-season batch with ties calibrated to an observed draw rate.
Usage: python3 ucl_batch_drawrate.py DRAWS GAMES [n_sims] [seed]
e.g.   python3 ucl_batch_drawrate.py 7 72      (2026-27 UCL after 4 matchdays)
"""
import random
import sys

import ucl_sim as S
import ucl_batch as B


def calibrate(target, seeds=500):
    """TIE_SCALE so the average per-game tie probability equals `target`."""
    S.TIE_SCALE = 1.0
    tot = n = 0
    for seed in range(seeds):
        games, _ = S.make_season_schedule(random.Random(seed))
        for h, a in games:
            tot += S.match_probs(S.tier_of(h), S.tier_of(a))[1]
            n += 1
    return target / (tot / n)


if __name__ == "__main__":
    draws, games = int(sys.argv[1]), int(sys.argv[2])
    target = draws / games
    S.TIE_SCALE = calibrate(target)
    print(f"Observed draw rate {draws}/{games} = {target:.1%} -> TIE_SCALE = {S.TIE_SCALE:.4f}\n")
    sys.argv = [sys.argv[0]] + sys.argv[3:]
    B.main()
