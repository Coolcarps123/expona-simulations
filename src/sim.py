import argparse, json
import numpy as np, pandas as pd

from .mechanisms import get_tau
from .windows import VolumeWindows
from .market import Market
from .agents import noise, mean_reverter
from .metrics import summarize

def run_sim(steps=20000, seed=1, delta=15, mechanism="adaptive",
            L_mult=10.0, kappa_mr=0.2, tau_params=None):
    rng = np.random.default_rng(seed)
    tau_params = tau_params or {}
    tau_fn = get_tau(mechanism, **tau_params)

    windows = VolumeWindows(delta_seconds=delta)
    mkt = Market(price0=1.0, supply=1_000_000.0, baseline_daily_vol=50_000.0, L_mult=L_mult)

    # EMA for price baseline (~30d)
    hl_steps = (30*86400)//delta
    ema_alpha = np.log(2)/hl_steps
    pbar = mkt.price

    rows = []
    seconds = 0
    for t in range(steps):
        scale = mkt.baseline_daily_vol / (86400/delta)
        x = 0.7*noise(rng, scale) + 0.3*mean_reverter(rng, mkt.price, pbar, kappa=kappa_mr, scale=scale)

        V24 = windows.V24()
        V30 = windows.V30()
        r = (V24 / V30) if V30 > 0 else 1.0
        tau = tau_fn(r)

        mkt.execute(x)
        pbar = ema_alpha*mkt.price + (1-ema_alpha)*pbar
        windows.step(abs(x))

        rows.append({"t": t, "sec": seconds, "price": mkt.price, "V24": V24, "V30": V30, "r": r, "tau": tau})
        seconds += delta

    df = pd.DataFrame(rows)
    meta = {"params": dict(steps=steps, seed=seed, delta=delta, mechanism=mechanism,
                           L_mult=L_mult, kappa_mr=kappa_mr, tau_params=tau_params)}
    meta["summary"] = summarize(df, delta_seconds=delta)
    return df, meta

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--delta", type=int, default=15)
    ap.add_argument("--mechanism", type=str, default="adaptive",
                    choices=["off","flat","linear","adaptive"])
    ap.add_argument("--L", type=float, default=10.0)
    ap.add_argument("--kappa_mr", type=float, default=0.2)
    ap.add_argument("--tau_params", type=str, default="{}")
    args = ap.parse_args()

    df, meta = run_sim(steps=args.steps, seed=args.seed, delta=args.delta,
                       mechanism=args.mechanism, L_mult=args.L, kappa_mr=args.kappa_mr,
                       tau_params=json.loads(args.tau_params))
    df.to_csv("out/trace.csv", index=False)
    with open("out/summary.json","w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta["summary"], indent=2))

if __name__ == "__main__":
    main()
