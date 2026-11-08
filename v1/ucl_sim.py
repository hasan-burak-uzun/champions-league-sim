"""
Champions League league-phase simulator (36 teams, 4 pots of 9, 8 matchdays).

Rules modelled
- Each team plays 8 games: 2 opponents from EACH pot (own pot included),
  one at home and one away  -> 4 home + 4 away, 144 games total.
- One game per team per week, 8 weeks.
- Win = 3 pts, tie = 1 pt, loss = 0 pts (no goals modelled).

Usage:  python3 ucl_sim.py [seed]
"""
import math
import random
import sys

# --------------------------------------------------------------------------
# PARAMETERS  (edit these)
# --------------------------------------------------------------------------
N_POTS = 4
TEAMS_PER_POT = 9
N_WEEKS = 8
WIN_PTS, DRAW_PTS, LOSS_PTS = 3, 1, 0

# Two factors drive every match:
#   1. POT STRENGTH  - the gap between the two pots (pot 1 strongest)
#   2. HOME ADVANTAGE - added to the home team
#
#   x = POT_STRENGTH[home pot] - POT_STRENGTH[away pot] + HOME_ADV
#   P(tie)            = TIE_BASE - TIE_SLOPE * |x|   (lopsided games draw less)
#   win : loss odds   = e^x   (applied to the non-tie probability)
#
# Calibrated to your examples:
#   v1 (original anchors): pot steps 0.378, HOME_ADV 0.811
#        pot 1 home vs pot 4 -> 70/20/10, pot 1 home vs pot 1 -> 45/35/20
#   v2: bigger gaps between pots (step 0.45), smaller home edge (0.65)
#   v3 (current): pot step 0.55, and a wide gap inside each pot (SUBGAP 0.35)
POT_STRENGTH = [1.65, 1.10, 0.55, 0.0]
HOME_ADV = 0.65

# Each pot is split into two difficulty groups -> 8 tiers in total.
# In every pot the first UPPER_PER_POT teams (e.g. P1-1..P1-4) are the stronger
# group ('a'); the rest ('b') are weaker. SUBGAP is the strength gap between the
# two groups of a pot (a pot-to-pot step is 0.55, so 0.35 is about two thirds of it).
UPPER_PER_POT = 4
SUBGAP = 0.35
N_TIERS = 2 * N_POTS

# Fraction of the original tie probability that is kept. The removed tie mass is
# split evenly: half to a home win, half to an away win (so the win-vs-loss
# balance of every matchup is unchanged). 1.0 = previous model, 0.5 = half the ties.
TIE_SCALE = 0.5
TIE_BASE = 0.457
TIE_SLOPE = 0.1322

# Override any single cell: OVERRIDE[(home_pot, away_pot)] = (pW, pT, pL) from
# the HOME team's view (tiers 0-indexed: 0 = pot 1 upper, 1 = pot 1 lower, ...).
OVERRIDE = {}


def tier_of(t):
    """0..7: tier 0 = pot 1 upper group, 1 = pot 1 lower group, 2 = pot 2 upper, ..."""
    return pot_of(t) * 2 + (0 if t % TEAMS_PER_POT < UPPER_PER_POT else 1)


def tier_label(k):
    return f"{k // 2 + 1}{'ab'[k % 2]}"


def tier_strength(k):
    return POT_STRENGTH[k // 2] + (SUBGAP / 2 if k % 2 == 0 else -SUBGAP / 2)


def match_probs(home_tier, away_tier):
    """(P(home win), P(tie), P(home loss)) for tiers 0..7"""
    if (home_tier, away_tier) in OVERRIDE:
        return OVERRIDE[(home_tier, away_tier)]
    x = tier_strength(home_tier) - tier_strength(away_tier) + HOME_ADV
    tie = max(0.05, TIE_BASE - TIE_SLOPE * abs(x))
    odds = math.exp(x)
    win = (1.0 - tie) * odds / (1.0 + odds)
    freed = tie * (1.0 - TIE_SCALE)
    tie -= freed
    win += freed / 2.0
    return win, tie, 1.0 - tie - win


# --------------------------------------------------------------------------
# FIXTURES
# --------------------------------------------------------------------------
def pot_of(t):
    return t // TEAMS_PER_POT


def name_of(t):
    return f"P{pot_of(t) + 1}-{t % TEAMS_PER_POT + 1}"


def build_fixtures(rng):
    """Return list of (home, away). Every team: 2 opponents per pot, 1 home + 1 away."""
    n = TEAMS_PER_POT
    pots = [[p * n + k for k in range(n)] for p in range(N_POTS)]
    games = []
    for a in range(N_POTS):
        A = pots[a][:]
        rng.shuffle(A)
        # same pot: a 9-cycle, each team hosts the next one -> 1 home + 1 away
        for k in range(n):
            games.append((A[k], A[(k + 1) % n]))
        for b in range(a + 1, N_POTS):
            B = pots[b][:]
            rng.shuffle(B)
            # A[k] hosts B[k]; B[k] hosts A[k+1]
            for k in range(n):
                games.append((A[k], B[k]))
                games.append((B[k], A[(k + 1) % n]))
    return games


def schedule_weeks(games, rng, n_weeks=N_WEEKS, n_teams=N_POTS * TEAMS_PER_POT):
    """Edge-colour the fixture graph with n_weeks colours (Kempe-chain repair).
    Returns list of weeks (each a list of game indices) or None on failure."""
    col_at = [dict() for _ in range(n_teams)]  # team -> {week: game idx}
    week_of = [None] * len(games)

    def other(e, t):
        h, a = games[e]
        return a if t == h else h

    order = list(range(len(games)))
    rng.shuffle(order)
    for e in order:
        u, v = games[e]
        free_u = [c for c in range(n_weeks) if c not in col_at[u]]
        free_v = [c for c in range(n_weeks) if c not in col_at[v]]
        common = [c for c in free_u if c in free_v]
        if common:
            c = rng.choice(common)
        else:
            a, b = free_u[0], free_v[0]  # a free at u (used at v); b free at v
            path, cur, c2, seen = [], v, a, {v}
            while c2 in col_at[cur]:
                pe = col_at[cur][c2]
                path.append(pe)
                cur = other(pe, cur)
                if cur in seen:
                    return None
                seen.add(cur)
                c2 = b if c2 == a else a
            if u in seen:
                return None
            old = [(pe, week_of[pe]) for pe in path]
            for pe, oc in old:
                h, aw = games[pe]
                del col_at[h][oc]
                del col_at[aw][oc]
            for pe, oc in old:
                nc = b if oc == a else a
                h, aw = games[pe]
                col_at[h][nc] = pe
                col_at[aw][nc] = pe
                week_of[pe] = nc
            c = a
        h, aw = games[e]
        col_at[h][c] = e
        col_at[aw][c] = e
        week_of[e] = c
    weeks = [[] for _ in range(n_weeks)]
    for e, w in enumerate(week_of):
        weeks[w].append(e)
    return weeks


def make_season_schedule(rng):
    while True:
        games = build_fixtures(rng)
        weeks = schedule_weeks(games, rng)
        if weeks and all(len(w) == len(games) // N_WEEKS for w in weeks):
            return games, weeks


# --------------------------------------------------------------------------
# SIMULATION
# --------------------------------------------------------------------------
def simulate_season(rng, verbose_weeks=False):
    n_teams = N_POTS * TEAMS_PER_POT
    games, weeks = make_season_schedule(rng)
    pts = [0] * n_teams
    rec = [[0, 0, 0] for _ in range(n_teams)]  # [W, T, L]
    for w, idxs in enumerate(weeks, 1):
        if verbose_weeks:
            print(f"\n--- Week {w} ---")
        for e in idxs:
            h, a = games[e]
            pw, pt, _ = match_probs(tier_of(h), tier_of(a))
            r = rng.random()
            if r < pw:
                pts[h] += WIN_PTS
                pts[a] += LOSS_PTS
                rec[h][0] += 1
                rec[a][2] += 1
                res = f"{name_of(h)} wins"
            elif r < pw + pt:
                pts[h] += DRAW_PTS
                pts[a] += DRAW_PTS
                rec[h][1] += 1
                rec[a][1] += 1
                res = "tie"
            else:
                pts[a] += WIN_PTS
                pts[h] += LOSS_PTS
                rec[a][0] += 1
                rec[h][2] += 1
                res = f"{name_of(a)} wins"
            if verbose_weeks:
                print(f"  {name_of(h):>5} (H) vs {name_of(a):<5} -> {res}")
    return games, weeks, pts, rec


def verify(games, weeks):
    n_teams = N_POTS * TEAMS_PER_POT
    home = [0] * n_teams
    away = [0] * n_teams
    per_pot = [[[0, 0] for _ in range(N_POTS)] for _ in range(n_teams)]  # [home, away]
    for h, a in games:
        home[h] += 1
        away[a] += 1
        per_pot[h][pot_of(a)][0] += 1
        per_pot[a][pot_of(h)][1] += 1
    assert all(home[t] == 4 and away[t] == 4 for t in range(n_teams)), "home/away split"
    assert all(per_pot[t][p] == [1, 1] for t in range(n_teams) for p in range(N_POTS)), "pot split"
    assert len({frozenset(g) for g in games}) == len(games), "duplicate pairing"
    for w in weeks:
        teams = [t for e in w for t in games[e]]
        assert len(teams) == len(set(teams)) == n_teams, "team plays once per week"


def print_matrix():
    print("HOME team's Win/Tie/Loss %  (rows = home tier, cols = away tier;"
          " 'a' = upper group, 'b' = lower group of each pot)")
    print("      " + "".join(f"{'vs ' + tier_label(j):>11}" for j in range(N_TIERS)))
    for i in range(N_TIERS):
        cells = ""
        for j in range(N_TIERS):
            w, t, l = match_probs(i, j)
            cells += f"{w * 100:.0f}/{t * 100:.0f}/{l * 100:.0f}".rjust(11)
        print(f"  {tier_label(i):>3} " + cells)


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    show_weeks = "--weeks" in sys.argv
    rng = random.Random(seed)
    print_matrix()
    games, weeks, pts, rec = simulate_season(rng, show_weeks)
    verify(games, weeks)
    print("\nSchedule check passed: 144 games, 8 weeks x 18 games, every team 8 games "
          "(4H/4A, one home + one away vs each pot).")

    n_teams = len(pts)
    # sort: points, then wins, then random (no goals modelled)
    order = sorted(range(n_teams), key=lambda t: (-pts[t], -rec[t][0], rng.random()))
    print(f"\nFINAL STANDINGS (seed {seed}) -- ties after points & wins broken randomly")
    print(f"{'Pos':>3}  {'Team':<6} {'W':>2} {'T':>2} {'L':>2} {'Pts':>3}  Zone")
    for pos, t in enumerate(order, 1):
        zone = "Top 8 (R16)" if pos <= 8 else ("Playoff" if pos <= 24 else "Out")
        w, d, l = rec[t]
        print(f"{pos:>3}  {name_of(t):<6} {w:>2} {d:>2} {l:>2} {pts[t]:>3}  {zone}")

    print("\nBy pot:")
    for p in range(N_POTS):
        ts = [t for t in range(n_teams) if pot_of(t) == p]
        avg_pts = sum(pts[t] for t in ts) / len(ts)
        avg_rank = sum(order.index(t) + 1 for t in ts) / len(ts)
        top8 = sum(1 for t in ts if order.index(t) < 8)
        print(f"  Pot {p + 1}: avg pts {avg_pts:5.2f}, avg rank {avg_rank:5.1f}, in top 8: {top8}")


if __name__ == "__main__":
    main()
