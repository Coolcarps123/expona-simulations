import argparse, numpy as np, pandas as pd, os
from sklearn.utils import resample
from src.sim import run_sim

def run_volatility_grid(fast=True):
    # parameter grid
    mechanisms = ["off", "linear", "flat", "adaptive"]
    deltas = [15] if fast else [1, 5, 15, 60]
    seeds = range(1, 6) if fast else range(1, 31)
    L = 10.0

    rows = []
    for mech in mechanisms:
        for d in deltas:
            for seed in seeds:
                df, meta = run_sim(
                    steps=20000 if fast else 60000,
                    seed=seed, delta=d, mechanism=mech, L_mult=L
                )
                summary = meta["summary"]
                summary.update({
                    "mechanism": mech,
                    "delta": d,
                    "L": L,
                    "seed": seed
                })
                rows.append(summary)

    out = pd.DataFrame(rows)
    os.makedirs("out", exist_ok=True)
    out.to_csv("out/volatility_grid.csv", index=False)
    return out


def compute_bootstrap_summary(df):
    """Compute mean σ, CI, and reduction % vs off."""
    def boot_ci(x):
        samples = [np.mean(resample(x)) for _ in range(500)]
        return np.percentile(samples, [2.5, 97.5])

    grp = df.groupby("mechanism")["vol_annualized"]
    mean_sigma = grp.mean()
    ci = grp.apply(boot_ci)

    summary = pd.DataFrame({
        "mechanism": mean_sigma.index,
        "mean_sigma": mean_sigma.values,
        "ci_low": [c[0] for c in ci.values],
        "ci_high": [c[1] for c in ci.values],
    })
    base = summary.loc[summary["mechanism"] == "off", "mean_sigma"].iloc[0]
    summary["reduction_pct"] = 100 * (base - summary["mean_sigma"]) / base
    summary.to_csv("out/volatility_summary.csv", index=False)
    return summary


def plot_summary(summary):
    import matplotlib.pyplot as plt
    plt.figure(figsize=(7, 5))
    plt.bar(summary["mechanism"], summary["mean_sigma"], yerr=[
        summary["mean_sigma"] - summary["ci_low"],
        summary["ci_high"] - summary["mean_sigma"],
    ], capsize=4)
    plt.title("Volatility by Mechanism (95% CI)")
    plt.ylabel("Annualized σ")
    plt.tight_layout()
    plt.savefig("out/volatility_summary.png")
    plt.show()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", type=str, default="volatility")
    ap.add_argument("--fast", action="store_true")
    args = ap.parse_args()

    df = run_volatility_grid(fast=args.fast)
    summary = compute_bootstrap_summary(df)
    print("\n=== VOLATILITY SUMMARY ===")
    print(summary.round(6))
    plot_summary(summary)


if __name__ == "__main__":
    main()
