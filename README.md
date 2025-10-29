# Expona — Volatility Reduction Proof (Clean Start)

This repo isolates one claim: **Adaptive transaction taxation reduces realized volatility** versus baselines.

## Quick start
```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Smoke test
python -m src.sim --steps 20000 --mechanism adaptive --delta 15 --seed 1

# Volatility comparison grid
python -m src.experiments --preset volatility --fast
```
Outputs under `out/` and plots under `out/plots/`.
