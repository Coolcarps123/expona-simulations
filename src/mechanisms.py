import numpy as np

def tau_off(r, **kwargs):
    return 0.0

def tau_flat(r, tau0=0.0025, **kwargs):
    return tau0  # 0.25%

def tau_linear(r, k=0.001, tau_cap=0.05, **kwargs):
    return float(min(k*r, tau_cap))

class TauAdaptive:
    def __init__(self, alpha=1.8, beta=2.0, gamma=2.5, tau_min=0.0, tau2=0.01, tau5=0.03, tau_cap=0.30):
        self.alpha, self.beta, self.gamma = alpha, beta, gamma
        self.tau_min, self.tau2, self.tau5, self.tau_cap = tau_min, tau2, tau5, tau_cap
        self.a = (self.tau2 - self.tau_min)/(2.0**self.alpha) if self.tau2>self.tau_min else 0.0
        self.s2 = self.a*self.alpha*(2.0**(self.alpha-1.0))
        self.b = max(0.0, (self.tau5 - self.tau2 - 3*self.s2) / (3.0**self.beta))
        self.s5 = self.s2 + self.b*self.beta*(3.0**(self.beta-1.0))
        delta=1.0
        self.c = max(0.0, (self.tau_cap - self.tau5 - self.s5*delta) / (delta**self.gamma))

    def __call__(self, r):
        if r <= 2.0:
            val = self.tau_min + self.a*(r**self.alpha)
        elif r <= 5.0:
            x = r-2.0
            val = self.tau2 + self.s2*x + self.b*(x**self.beta)
        else:
            x = r-5.0
            val = self.tau5 + self.s5*x + self.c*(x**self.gamma)
        return float(min(max(val, 0.0), self.tau_cap))

def get_tau(mechanism:str, **kwargs):
    m = mechanism.lower()
    if m == "off":     return tau_off
    if m == "flat":    return lambda r: tau_flat(r, **kwargs)
    if m == "linear":  return lambda r: tau_linear(r, **kwargs)
    if m == "adaptive":return TauAdaptive(**kwargs)
    raise ValueError(f"unknown mechanism: {mechanism}")
