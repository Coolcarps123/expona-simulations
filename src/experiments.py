import argparse, json, os
import numpy as np, pandas as pd
from .sim import run_sim

def run_volatility_grid(fast=False):
    steps = 20000 if fast else 60000
    seeds = [1,2,3,4,5] if fast else list(range(1,31))
    deltas = [15] if fast else [1,5,15,60]
    mechanisms = [
        ("off", {}),
        ("flat", {"tau0":0.0025}),
        ("linear", {"k":0.001, "tau_cap":0.05}),
        ("adaptive", {"alpha":1.8,"beta":2.0,"gamma":2.5,"tau_min":0.0,"tau2":0.01,"tau5":0.03,"tau_cap":0.30}),
    ]
    Ls = [10.0]

    rows = []
    for mech, params in mechanisms:
        for d in deltas:
            for L in Ls:
                for seed in seeds:
                    df, meta = run_sim(steps=steps, seed=seed, delta=d, mechanism=mech, L_mult=L, tau_params=params)
                    s = meta["summary"]
                    s.update({"mechanism": mech, "delta": d, "L": L, "seed": seed})
                    rows.append(s)

    out = pd.DataFrame(rows)
    os.makedirs("out", exist_ok=True)
    out.to_csv("out/volatility_grid.csv", index=False)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", type=str, default="volatility")
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()
    if args.preset == "volatility":
        out = run_volatility_grid(fast=args.fast)
        print(out.groupby(["mechanism","delta"])["vol_annualized"].mean())
    else:
        raise ValueError("unknown preset")

if __name__ == "__main__":
    main()
