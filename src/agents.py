import numpy as np

def noise(rng, scale):
    size = rng.lognormal(mean=np.log(scale), sigma=0.5)
    return size if rng.random() > 0.5 else -size

def mean_reverter(rng, price, pbar, kappa, scale):
    dev = (pbar - price)/max(1e-9, pbar)
    base = kappa * dev * scale
    return base * rng.normal(1.0, 0.2)
