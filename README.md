# Champions League league-phase simulator

36 teams, 4 pots of 9, 8 matchdays. Each team plays 2 opponents from each pot
(one home, one away), so 4 home + 4 away. Win 3, draw 1, loss 0.

## Live page
`index.html` is a single-file interactive simulator (sliders, presets for Champions League and
Europa League, 1,000-season runs). Publish with `publish.bat` (GitHub Pages).

## Model (v2, fitted to bookmaker odds)
strength gap x = strength(home) - strength(away) + home advantage;
P(draw) = TIE0 - TIE_FADE*|x|; P(home win) = (1 - P(draw)) / (1 + e^-x).
Team strength = pot strength +/- half the group gap + a random per-season offset.
The "Europa League" preset sits halfway between the Champions League fit and a thin fit
to 13 Europa League games (matchdays 3-4).

## Python files
- `ucl_sim.py` - one season: fixtures, 8-week schedule, match odds, standings. Parameters at top.
- `ucl_batch.py` - 1,000 perturbed seasons; points distribution at 8th/16th/24th. `python ucl_batch.py 1000 2026`
- `ucl_batch_drawrate.py` - same, calibrated to an observed draw rate. `python ucl_batch_drawrate.py 7 72`
- `ucl_tiers.py` - per-tier average points and top-8 / playoff / out rates.
- `check_tables.py` - sanity checks on real UCL/UEL tables.
- `market_data.py`, `fit_market.py`, `evaluate_fit.py`, `compare_odds.py` - bookmaker odds (57 UCL games, MD1-4) and the fit/validation.
- `upcoming_odds.py`, `compare_upcoming.py` - out-of-sample check on matchday 5 odds.
- `europa/` - Europa League odds (13 games) and fit.
- `v1/` - the earlier hand-set version of the scripts.
