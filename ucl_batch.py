"""
Run many Champions League league-phase seasons, each with slightly perturbed
probabilities, and report the points distribution at chosen positions.

Usage: python3 ucl_batch.py [n_sims] [seed]
"""
import csv
import random
import statistics
import sys
from collections import Counter

import ucl_sim as S

# --------------------------------------------------------------------------
# PERTURBATION SETTINGS  (std-dev of Gaussian noise added to each parameter,
# redrawn once per simulated season)
# --------------------------------------------------------------------------
SD_STRENGTH = 0.10   # each pot's strength (the fit's standard error is ~0.2)
SD_HOME_ADV = 0.08   # home advantage (fit: 0.60, standard error ~0.09)
SD_TIE_BASE = 0.01   # draw probability in an even match (base 0.275)

POSITIONS = [8, 16, 24]

BASE_STRENGTH = list(S.POT_STRENGTH)
BASE_HOME = S.HOME_ADV
BASE_TIE = S.TIE0


def perturb(rng):
    S.POT_STRENGTH = [s + rng.gauss(0, SD_STRENGTH) for s in BASE_STRENGTH]
    S.HOME_ADV = BASE_HOME + rng.gauss(0, SD_HOME_ADV)
    S.TIE0 = BASE_TIE + rng.gauss(0, SD_TIE_BASE)


def pct(sorted_vals, q):
    i = (len(sorted_vals) - 1) * q
    lo, hi = int(i), min(int(i) + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (i - lo)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    master = random.Random(seed)

    at_pos = {p: [] for p in POSITIONS}
    rows = []
    for i in range(n):
        perturb(master)
        rng = random.Random(master.random())
        games, weeks, pts, rec = S.simulate_season(rng)
        ranked = sorted(pts, reverse=True)  # points at a position don't depend on tiebreaks
        for p in POSITIONS:
            at_pos[p].append(ranked[p - 1])
        pot_avg = [
            sum(pts[t] for t in range(S.N_POTS * S.TEAMS_PER_POT) if S.pot_of(t) == k)
            / S.TEAMS_PER_POT
            for k in range(S.N_POTS)
        ]
        rows.append([i + 1] + [ranked[p - 1] for p in POSITIONS] + [round(x, 3) for x in pot_avg])

    with open("ucl_batch_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sim"] + [f"pts_pos{p}" for p in POSITIONS] +
                   [f"avg_pts_pot{k + 1}" for k in range(S.N_POTS)])
        w.writerows(rows)

    print(f"{n} simulated seasons, seed {seed}. Per-season noise (sd): "
          f"pot strength {SD_STRENGTH}, home adv {SD_HOME_ADV}, tie base {SD_TIE_BASE}\n")

    print(f"{'Position':>9} {'Mean':>6} {'SD':>5} {'Min':>4} {'P5':>5} {'P25':>5} "
          f"{'Median':>6} {'P75':>5} {'P95':>5} {'Max':>4}")
    for p in POSITIONS:
        v = sorted(at_pos[p])
        print(f"{p:>9} {statistics.mean(v):6.2f} {statistics.pstdev(v):5.2f} {v[0]:>4} "
              f"{pct(v, .05):5.1f} {pct(v, .25):5.1f} {pct(v, .5):6.1f} {pct(v, .75):5.1f} "
              f"{pct(v, .95):5.1f} {v[-1]:>4}")

    cnt = {p: Counter(at_pos[p]) for p in POSITIONS}
    allpts = sorted(set().union(*[set(c) for c in cnt.values()]))
    print("\nShare of simulations with exactly this many points at each position:")
    print(f"{'Pts':>4} " + "".join(f"{'#' + str(p):>9}" for p in POSITIONS))
    for x in allpts:
        print(f"{x:>4} " + "".join(f"{cnt[p][x] / n:>9.1%}" for p in POSITIONS))

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 4.5))
        width = 0.27
        colors = ["#2a6fbb", "#e08a1e", "#7a7a7a"]
        for k, p in enumerate(POSITIONS):
            ax.bar([x + (k - 1) * width for x in allpts],
                   [cnt[p][x] / n * 100 for x in allpts],
                   width, label=f"{p}th place", color=colors[k])
        ax.set_xlabel("Points after 8 matchdays")
        ax.set_ylabel("% of simulated seasons")
        ax.set_title(f"Points at 8th / 16th / 24th place ({n} seasons)")
        ax.legend(frameon=False)
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig("ucl_points_distribution.png", dpi=150)
        print("\nSaved chart: ucl_points_distribution.png")
    except ImportError:
        print("\n(matplotlib not installed; skipped chart)")


if __name__ == "__main__":
    main()
