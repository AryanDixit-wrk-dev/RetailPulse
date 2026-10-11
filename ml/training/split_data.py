from pathlib import Path

import pandas as pd


FEATURE_FILE = Path("data/processed/ml_sales_features.csv")
TRAIN_FILE = Path("data/processed/ml_train.csv")
TEST_FILE = Path("data/processed/ml_test.csv")


def split_data(
    df: pd.DataFrame,
    test_days: int = 124,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split the dataset chronologically by date."""

    df = df.copy()
    df["full_date"] = pd.to_datetime(df["full_date"])

    dates = sorted(df["full_date"].unique())

    split_date = dates[-test_days]

    train = df[df["full_date"] < split_date].copy()
    test = df[df["full_date"] >= split_date].copy()

    return train, test


def main():
    df = pd.read_csv(FEATURE_FILE)

    train, test = split_data(df)

    TRAIN_FILE.parent.mkdir(parents=True, exist_ok=True)

    train.to_csv(TRAIN_FILE, index=False)
    test.to_csv(TEST_FILE, index=False)

    print(f"Training rows: {len(train):,}")
    print(f"Training dates: {train['full_date'].min().date()} to {train['full_date'].max().date()}")

    print(f"Test rows: {len(test):,}")
    print(f"Test dates: {test['full_date'].min().date()} to {test['full_date'].max().date()}")

    print(f"Training file: {TRAIN_FILE}")
    print(f"Test file: {TEST_FILE}")


if __name__ == "__main__":
    main()