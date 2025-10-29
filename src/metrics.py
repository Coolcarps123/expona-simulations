import numpy as np, pandas as pd

def realized_vol(prices, delta_seconds=15):
    r = np.diff(np.log(np.maximum(prices, 1e-12)))
    sec_per_day = 86400.0 / delta_seconds
    return float(np.std(r) * (sec_per_day**0.5))

def kurtosis(prices):
    r = np.diff(np.log(np.maximum(prices, 1e-12)))
    m2 = np.mean((r - r.mean())**2)
    m4 = np.mean((r - r.mean())**4)
    return float(m4 / (m2**2) - 3.0)

def summarize(trace_df, delta_seconds=15):
    return {
        "vol_annualized": realized_vol(trace_df["price"].values, delta_seconds),
        "kurtosis": kurtosis(trace_df["price"].values),
        "mean_tau": float(trace_df["tau"].mean()),
        "p95_tau": float(trace_df["tau"].quantile(0.95)),
        "avg_r": float(trace_df["r"].mean())
    }
