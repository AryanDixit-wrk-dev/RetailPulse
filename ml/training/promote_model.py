from pathlib import Path

import joblib
import pandas as pd


CURRENT_MODEL_FILE = Path("models/random_forest_sales.joblib")
CANDIDATE_MODEL_FILE = Path("models/random_forest_sales_candidate.joblib")
EVALUATION_FILE = Path("reports/retraining_evaluation.csv")
DECISION_FILE = Path("reports/model_promotion_decision.txt")


def load_evaluation() -> pd.DataFrame:
    """Load current and candidate model evaluation results."""
    return pd.read_csv(EVALUATION_FILE)


def decide_promotion(df: pd.DataFrame) -> str:
    """Decide whether the candidate model should be promoted."""

    current = df.loc[
        df["model"] == "current"
    ].iloc[0]

    candidate = df.loc[
        df["model"] == "candidate"
    ].iloc[0]

    if candidate["mae"] < current["mae"]:
        return "PROMOTE"

    if candidate["mae"] > current["mae"]:
        return "REJECT"

    return "KEEP_CURRENT"


def promote_candidate():
    """Replace the current model with the candidate model."""
    model = joblib.load(CANDIDATE_MODEL_FILE)
    joblib.dump(model, CURRENT_MODEL_FILE)


def main():
    evaluation = load_evaluation()
    decision = decide_promotion(evaluation)

    print("Model promotion evaluation")
    print(f"Decision: {decision}")

    if decision == "PROMOTE":
        promote_candidate()
        print("Candidate model promoted successfully.")

    elif decision == "KEEP_CURRENT":
        print("Candidate model is unchanged.")
        print("Current production model retained.")

    else:
        print("Candidate model performed worse.")
        print("Current production model retained.")

    DECISION_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    DECISION_FILE.write_text(
        f"Decision: {decision}\n",
        encoding="utf-8",
    )

    print(f"Decision saved: {DECISION_FILE}")


if __name__ == "__main__":
    main()