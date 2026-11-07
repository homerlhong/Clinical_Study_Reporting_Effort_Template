"""Generate clearly labelled synthetic data; never substitute for patient data."""

import numpy as np
import pandas as pd


FEATURES = [
    "age_years",
    "max_diameter_mm",
    "cavernous_sinus_invasion",
    "functional_tumor",
    "postoperative_residual",
    "early_biochemical_response",
]
OUTCOME = "progression_or_retreatment_3y"


def make_synthetic_cohort(n: int = 500, seed: int = 42) -> pd.DataFrame:
    """Return simulated records for pipeline development only."""
    rng = np.random.default_rng(seed)
    age = rng.normal(51, 13, n).clip(18, 90)
    diameter = rng.lognormal(mean=3.1, sigma=0.45, size=n).clip(3, 70)
    invasion = rng.binomial(1, 1 / (1 + np.exp(-(diameter - 22) / 7)))
    functional = rng.binomial(1, 0.55, n)
    residual_probability = 1 / (1 + np.exp(-(-2.0 + 1.3 * invasion + 0.03 * diameter)))
    residual = rng.binomial(1, residual_probability)
    biochemical_response = rng.binomial(1, 1 / (1 + np.exp(-(-0.2 - 0.8 * residual + 0.4 * functional))))
    log_odds = -3.4 + 1.1 * invasion + 1.25 * residual - 0.9 * biochemical_response + 0.018 * diameter
    outcome = rng.binomial(1, 1 / (1 + np.exp(-log_odds)))
    return pd.DataFrame({
        "age_years": age.round(1),
        "max_diameter_mm": diameter.round(1),
        "cavernous_sinus_invasion": invasion,
        "functional_tumor": functional,
        "postoperative_residual": residual,
        "early_biochemical_response": biochemical_response,
        OUTCOME: outcome,
    })
