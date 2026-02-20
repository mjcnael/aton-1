import uuid
import pandas as pd


def clean_transactions(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()

    # Drop rows with missing critical fields
    df = df.dropna(subset=["client_id", "amount"])

    # Standardize date format and handle invalid dates
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df = df.dropna(subset=["transaction_date"])

    # Fill missing transaction_id with uuid
    df["transaction_id"] = df["transaction_id"].fillna(str(uuid.uuid4()))

    # Remove transactions with non-positive amounts
    df = df.loc[df["amount"] > 0]

    # Drop duplicates
    df = df.drop_duplicates(subset=["transaction_id"])

    # Fill missing values in categorical fields
    df["payment_method"] = df["payment_method"].fillna("Неизвестно")
    df["service"] = df["service"].fillna("Неизвестная услуга")
    df["city"] = df["city"].fillna("Неизвестный город")
    df["consultant"] = df["consultant"].fillna("Неизвестный консультант")

    df = df.reset_index(drop=True)

    return df


def clean_clients(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()

    # Drop rows with missing critical fields
    df = df.dropna(subset=["id"])

    # Fill missing values
    df["gender"] = df["gender"].fillna("Неизвестно")
    df["net_worth"] = df["net_worth"].fillna(0)

    df = df.reset_index(drop=True)

    return df


def merge_tables(transactions: pd.DataFrame, clients: pd.DataFrame) -> pd.DataFrame:
    merged_df = transactions.merge(
        clients, left_on="client_id", right_on="id", how="left", indicator=True
    )

    # Remove unmatched transactions
    unmatched_count = (merged_df["_merge"] != "both").sum()
    if unmatched_count > 0:
        print(f"Merge: {unmatched_count} unmatched transactions found.")
    merged_df = merged_df.loc[merged_df["_merge"] == "both"]
    merged_df = merged_df.drop(columns="_merge")

    return merged_df
