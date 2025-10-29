from src.mechanisms import get_tau
def test_compile():
    assert callable(get_tau("off"))
    assert callable(get_tau("flat", tau0=0.002))
    assert callable(get_tau("linear", k=0.001))
    assert callable(get_tau("adaptive", alpha=1.8, beta=2.0, gamma=2.5))
