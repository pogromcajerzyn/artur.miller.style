from pathlib import Path

import numpy as np
import pandas as pd


def get_strength_data() -> pd.DataFrame:
    """Read data from the csv file and return it as a pandas dataframe.

    Returns:
        pd.DataFrame: A pandas dataframe containing the strength data and additional statistics.

    """

    # Read the CSV file (limit to today)
    csv_path = Path(__file__).parent / "data.csv"
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"], format="%y-%m-%d")
    df = df.sort_values("date")
    today = pd.Timestamp.today().normalize()
    df = df[df["date"] <= today]

    exercises = ["bench", "deadlift", "squat"]

    # Validate that all data is 7 days apart
    invalid_mask = df["date"].diff()[1:] != pd.Timedelta(days=7)
    if invalid_mask.any():
        # Use .iloc[1:] to align with the mask
        invalid_rows = df.iloc[1:][invalid_mask]
        raise ValueError(
            "Dates are not 7 days apart in these rows:\n"
            + invalid_rows[["date"]].to_string()
        )

    # Exercise must be filled together with repetition number
    for ex in exercises:
        ex_r = f"{ex}_r"
        invalid_rows = df.loc[df[ex].notna() ^ df[ex_r].notna(), ["date", ex, ex_r]]
        assert (
            invalid_rows.empty
        ), f"Found rows where only one of {ex} or {ex_r} is filled:\n{invalid_rows.to_string()}"

    # Validate that the weight is given if there is any data in exercise fields
    mask_has_lift = df[exercises].notna().any(axis=1)
    mask_missing_weight = df["weight"].isna()
    invalid_rows = df[mask_has_lift & mask_missing_weight]
    assert invalid_rows.empty, (
        "Found rows with lifts but missing weight:\n"
        + invalid_rows[["date", "bench", "deadlift", "squat", "weight"]].to_string()
    )

    # Statistics
    for ex in exercises:
        # Get One Rep Max by using Landers formula (1985)
        df[f"{ex}_orm"] = (100 * df[ex]) / (101.3 - (2.67123 * df[f"{ex}_r"]))
        # Get a factor of weight to bodyweight
        df[f"{ex}_rel"] = df[f"{ex}_orm"] / df["weight"]

    # Weekly sum (power lvl) only if none are NaN, else NaN
    df["total_orm"] = df[["bench_orm", "deadlift_orm", "squat_orm"]].apply(
        lambda row: row.sum() if row.notna().all() else np.nan, axis=1
    )
    df["total_rel"] = df[["bench_rel", "deadlift_rel", "squat_rel"]].apply(
        lambda row: row.sum() if row.notna().all() else np.nan, axis=1
    )

    # Attendance statistics - full dataset
    present = df[exercises].notna().astype(int)
    cumulative_present = present.cumsum()
    cum_total_slots = pd.Series(range(1, len(df) + 1)) * len(exercises)
    df["attendance_so_far"] = cumulative_present.sum(axis=1) / cum_total_slots * 100

    # Attendance statistics - last 45 days
    attendance_last_days = []
    for idx, current_date in enumerate(df["date"]):
        window_start = current_date - pd.Timedelta(days=45)
        window_df = df.loc[(df["date"] > window_start) & (df["date"] <= current_date)]

        if len(window_df) == 0:
            attendance_last_days.append(0.0)
            continue

        total_slots = len(window_df) * len(exercises)
        present_count = window_df[exercises].notna().sum().sum()
        attendance_last_days.append(present_count / total_slots * 100)

    df["attendance_last_45d"] = attendance_last_days

    return df


if __name__ == "__main__":
    df = get_strength_data()
    print(df)
