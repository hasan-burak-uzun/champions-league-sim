"""
Tier-level results with the market-fitted model.
For each of the 8 tiers: average points and how often a team in that tier ends
top 8 / playoff (9-24) / eliminated (25-36).

Usage: python3 ucl_tiers.py [n_sims] [seed]
"""
import csv
import random
import sys

import ucl_sim as S
import ucl_batch as B

SCENARIOS = [("Market-fit", 1.0)]


def run(n, seed, tie_scale):
    master = random.Random(seed)
    n_teams = S.N_POTS * S.TEAMS_PER_POT
    size = [0] * S.N_TIERS
    for t in range(n_teams):
        size[S.tier_of(t)] += 1
    pts_sum = [0.0] * S.N_TIERS
    top8 = [0] * S.N_TIERS
    playoff = [0] * S.N_TIERS
    out = [0] * S.N_TIERS
    for _ in range(n):
        B.perturb(master)
        rng = random.Random(master.random())
        games, weeks, pts, rec = S.simulate_season(rng)
        order = sorted(range(n_teams), key=lambda t: (-pts[t], -rec[t][0], rng.random()))
        for pos, t in enumerate(order, 1):
            k = S.tier_of(t)
            pts_sum[k] += pts[t]
            if pos <= 8:
                top8[k] += 1
            elif pos <= 24:
                playoff[k] += 1
            else:
                out[k] += 1
    res = []
    for k in range(S.N_TIERS):
        d = n * size[k]  # team-seasons in this tier
        res.append((size[k], pts_sum[k] / d, top8[k] / d, playoff[k] / d, out[k] / d))
    return res


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    results = {name: run(n, seed, scale) for name, scale in SCENARIOS}

    print(f"{n} seasons per scenario, seed {seed}. Percentages = share of team-seasons in the tier.\n")
    hdr = f"{'Tier':>4} {'Teams':>5}  |"
    for name, _ in SCENARIOS:
        hdr += f" {name:^32} |"
    print(hdr)
    sub = f"{'':>4} {'':>5}  |" + (" " + f"{'Avg pts':>8}{'Top 8':>8}{'Playoff':>8}{'Out':>8}" + " |") * len(SCENARIOS)
    print(sub)
    for k in range(S.N_TIERS):
        line = f"{S.tier_label(k):>4} {results[SCENARIOS[0][0]][k][0]:>5}  |"
        for name, _ in SCENARIOS:
            _, avg, t8, po, ou = results[name][k]
            line += f" {avg:>8.2f}{t8:>8.1%}{po:>8.1%}{ou:>8.1%} |"
        print(line)

    with open("ucl_tier_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tier", "teams"] + [f"{name}_{m}" for name, _ in SCENARIOS
                                         for m in ("avg_pts", "top8", "playoff", "out")])
        for k in range(S.N_TIERS):
            row = [S.tier_label(k), results[SCENARIOS[0][0]][k][0]]
            for name, _ in SCENARIOS:
                row += [round(x, 4) for x in results[name][k][1:]]
            w.writerow(row)


if __name__ == "__main__":
    main()
