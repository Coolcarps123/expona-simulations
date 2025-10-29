class Market:
    def __init__(self, price0=1.0, supply=1_000_000.0, baseline_daily_vol=50_000.0, L_mult=10.0):
        self.price = price0
        self.supply = supply
        self.baseline_daily_vol = baseline_daily_vol
        self.L = L_mult * baseline_daily_vol

    def execute(self, x_notional: float) -> float:
        dp = x_notional / self.L
        self.price = max(1e-9, self.price + dp)
        return self.price
