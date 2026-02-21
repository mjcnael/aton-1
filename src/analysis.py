from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import json


def services_by_count(df: pd.DataFrame) -> pd.Series:
    return df["service"].value_counts()


def avg_transaction_amount_by_city(df: pd.DataFrame) -> pd.Series:
    return (
        pd.Series(df.groupby("city")["amount"].mean())
        .sort_values(ascending=False)
        .round(2)
    )


def services_by_transaction_amount(df: pd.DataFrame) -> pd.Series:
    return (
        pd.Series(df.groupby("service")["amount"].sum())
        .sort_values(ascending=False)
        .round(2)
    )


def payment_method_percentage(df: pd.DataFrame) -> pd.Series:
    counts = df["payment_method"].value_counts()
    return (counts / counts.sum() * 100).round(2)


def last_month_total_amount(df: pd.DataFrame) -> float:
    month_start = df["transaction_date"].max() - pd.DateOffset(months=1)
    last_month_df = df[df["transaction_date"] >= month_start]
    return round(float(last_month_df["amount"].sum().item()), 2)


def last_month_amount_by_service(df: pd.DataFrame) -> pd.Series:
    month_start = df["transaction_date"].max() - pd.DateOffset(months=1)
    last_month_df = df[df["transaction_date"] >= month_start]
    return (
        pd.Series(last_month_df.groupby("service")["amount"].sum())
        .sort_values(ascending=False)
        .round(2)
    )


def categorize_client_net_worth(capital: float) -> str:
    if capital < 100_000:
        return "Низкий капитал"
    elif capital <= 1_000_000:
        return "Средний капитал"
    else:
        return "Высокий капитал"


def client_net_worth_category_total_amount(df: pd.DataFrame) -> pd.Series:
    categories = df["net_worth"].apply(categorize_client_net_worth)
    return (
        pd.Series(df.groupby(categories)["amount"].sum())
        .sort_values(ascending=False)
        .round(2)
    )


def avg_transaction_amount_by_client_age(df: pd.DataFrame) -> pd.Series:
    return pd.Series(df.groupby("age")["amount"].mean()).round(2)


def forecast_next_month(df: pd.DataFrame) -> dict:
    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    monthly_df = (
        df.set_index("transaction_date")
        .resample("ME")
        .agg(
            count=("amount", "count"),
            amount=("amount", "sum"),
        )
        .reset_index()
    )

    monthly_df["time_index"] = range(len(monthly_df))

    X = monthly_df[["time_index"]].values

    model_count = LinearRegression()
    model_amount = LinearRegression()

    model_count.fit(X, monthly_df["count"])
    model_amount.fit(X, monthly_df["amount"])

    next_time = np.array([[monthly_df["time_index"].max() + 1]])

    next_count = model_count.predict(next_time)[0]
    next_amount = model_amount.predict(next_time)[0]

    return {
        "count": int(round(next_count)),
        "amount": float(round(next_amount)),
    }


def run_analysis(merged_df: pd.DataFrame, save_file_name: Path) -> dict:
    results = {
        "services_by_count": services_by_count(merged_df),
        "services_by_transaction_amount": services_by_transaction_amount(merged_df),
        "avg_transaction_amount_by_city": avg_transaction_amount_by_city(merged_df),
        "payment_method_percentage": payment_method_percentage(merged_df),
        "last_month_amount_by_service": last_month_amount_by_service(merged_df),
        "last_month_total_amount": last_month_total_amount(merged_df),
        "client_net_worth_category_total_amount": client_net_worth_category_total_amount(
            merged_df
        ),
        "avg_transaction_amount_by_client_age": avg_transaction_amount_by_client_age(
            merged_df
        ),
        "forecast_next_month": forecast_next_month(merged_df),
    }

    with open(save_file_name, "w", encoding="utf-8") as f:
        serializable = {}
        for k, v in results.items():
            if hasattr(v, "to_dict"):
                serializable[k] = v.to_dict()
            elif type(v) in [dict, int, float, str]:
                serializable[k] = v
        f.write(json.dumps(serializable, indent=2, ensure_ascii=False))
        print(f"Results saved: {save_file_name}")

    return results
