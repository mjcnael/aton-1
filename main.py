import os
import pandas as pd

from src.clean_data import clean_transactions, clean_clients, merge_tables
from src.analysis import run_analysis
from src.utils import audit_df
from src.generate_md_report import generate_md_report


def main() -> None:
    # Load tables
    transactions_file = "./data/transactions_data.xlsx"
    clients_file = "./data/clients_data.json"
    transactions_raw = pd.read_excel(transactions_file)
    clients_raw = pd.read_json(clients_file)

    output_dir = "./analysis_output"
    os.makedirs(output_dir, exist_ok=True)

    # Audit raw data
    audit_df(
        transactions_raw,
        save_file_name=f"{output_dir}/audit_raw_transactions.json",
        str_value_counts_exclude_col=["transaction_id", "client_id"],
    )
    audit_df(
        clients_raw,
        save_file_name=f"{output_dir}/audit_raw_clients.json",
        str_value_counts_exclude_col=["id"],
    )

    # Clean data
    transactions = clean_transactions(transactions_raw)
    clients = clean_clients(clients_raw)

    # Audit clean data
    audit_df(
        transactions,
        save_file_name=f"{output_dir}/audit_transactions.json",
        str_value_counts_exclude_col=["transaction_id", "client_id"],
    )
    audit_df(
        clients,
        save_file_name=f"{output_dir}/audit_clients.json",
        str_value_counts_exclude_col=["id"],
    )

    merged_df = merge_tables(transactions, clients)
    analysis_results = run_analysis(
        merged_df, save_file_name=f"{output_dir}/analysis_results.json"
    )

    generate_md_report(
        analysis_results,
        df=merged_df,
        save_path=f"{output_dir}/report.md",
    )


if __name__ == "__main__":
    main()
