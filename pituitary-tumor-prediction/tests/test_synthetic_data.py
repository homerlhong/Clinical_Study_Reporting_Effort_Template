from src.synthetic_data import FEATURES, OUTCOME, make_synthetic_cohort


def test_synthetic_cohort_has_contract_columns():
    cohort = make_synthetic_cohort(n=25)
    assert list(cohort.columns) == FEATURES + [OUTCOME]
    assert len(cohort) == 25
    assert cohort[OUTCOME].isin([0, 1]).all()
