from typing import Optional, Literal
import json
import pandas as pd
import numpy as np


def detect_outliers(
    series: pd.Series,
    method: Literal["iqr", "zscore"] = "iqr",
    zscore_threshold: float = 3.0,
    zscore_ddof: int = 0,
) -> dict:
    series = series.dropna()

    if series.empty:
        return {
            "count": 0,
            "percentage": 0.0,
            "lower_bound": None,
            "upper_bound": None,
        }

    lower: float | None = None
    upper: float | None = None
    outliers = pd.Series(dtype=series.dtype)

    if method == "iqr":
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        mask = (series < lower) | (series > upper)
        outliers = series[mask]

    elif method == "zscore":
        std = series.std(ddof=zscore_ddof)

        if std == 0 or np.isnan(std):
            return {
                "count": 0,
                "percentage": 0.0,
                "lower_bound": None,
                "upper_bound": None,
            }

        z_scores = (series - series.mean()) / std
        mask = np.abs(z_scores) > zscore_threshold
        outliers = series[mask]

    return {
        "count": int(len(outliers)),
        "percentage": float(len(outliers) / len(series)),
        "lower_bound": float(lower) if lower is not None else None,
        "upper_bound": float(upper) if upper is not None else None,
    }


def audit_df(
    df: pd.DataFrame,
    outlier_method: Literal["iqr", "zscore"] = "iqr",
    save_file_name: Optional[str] = None,
    str_value_counts_exclude_col: Optional[list[str]] = None,
) -> dict:
    audit = {}

    audit["rows"] = len(df)
    audit["columns"] = len(df.columns)
    audit["column_types"] = df.dtypes.astype(str).to_dict()

    missing_counts = df.isna().sum()
    audit["missing_total"] = int(missing_counts.sum())
    audit["missing_by_col"] = missing_counts.to_dict()
    audit["missing_ratio_by_col"] = (
        (missing_counts / len(df)).to_dict() if len(df) > 0 else {}
    )

    audit["duplicate_rows"] = int(df.duplicated().sum())
    audit["duplicate_rows_all"] = df[df.duplicated(keep=False)].shape[0]

    audit["duplicate_by_col"] = {
        col: int(df[col].duplicated().sum()) for col in df.columns
    }

    audit["constant_cols"] = [
        col for col in df.columns if df[col].nunique(dropna=False) <= 1
    ]

    numeric_df = df.select_dtypes(include=np.number)

    audit["numeric_outliers_by_col"] = {}
    audit["numeric_summary_by_col"] = {}

    for col, series in numeric_df.items():
        audit["numeric_summary_by_col"][col] = (
            series.describe().to_dict() if not series.dropna().empty else {}
        )

        audit["numeric_outliers_by_col"][col] = detect_outliers(
            series=series,
            method=outlier_method,
        )

    audit["str_summary_by_col"] = {}
    for col in df.select_dtypes(include="str").columns:
        if col in str_value_counts_exclude_col:
            continue
        counts = df[col].value_counts(dropna=False)
        audit["str_summary_by_col"][col] = {
            str(value): int(count) for value, count in counts.items()
        }

    if save_file_name is not None:
        with open(save_file_name, "w", encoding="utf-8") as f:
            json_str = json.dumps(audit, indent=2, ensure_ascii=False)
            f.write(json_str)
        print(f"Audit saved: {save_file_name}")

    return audit
