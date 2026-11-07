"""Train and report a baseline model on synthetic data only."""

from pathlib import Path
import json

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from src.synthetic_data import FEATURES, OUTCOME, make_synthetic_cohort


def main() -> None:
    cohort = make_synthetic_cohort()
    x, y = cohort[FEATURES], cohort[OUTCOME]
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, solver="liblinear"))
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    probabilities = cross_val_predict(model, x, y, cv=cv, method="predict_proba")[:, 1]
    report = {
        "data": "synthetic only; not clinically valid",
        "n": int(len(cohort)),
        "event_rate": float(y.mean()),
        "cross_validated_auc": float(roc_auc_score(y, probabilities)),
        "cross_validated_brier_score": float(brier_score_loss(y, probabilities)),
    }
    Path("artifacts").mkdir(exist_ok=True)
    Path("artifacts/baseline_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
