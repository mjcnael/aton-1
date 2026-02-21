import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style("dark")
sns.set_palette("muted")
plt.style.use("dark_background")


def plot_payment_method_pie(data: pd.Series, save_dir_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(
        data,
        labels=list(data.index),
        autopct="%1.1f%%",
        colors=sns.color_palette("Blues_d", n_colors=len(data))[::-1],
        startangle=140,
    )
    ax.set_title("Доля транзакций по способам оплаты")
    fig.tight_layout()
    file_path = save_dir_path / "payment_method_pie.png"
    fig.savefig(file_path)
    plt.close(fig)
    return file_path


def plot_services_by_transaction_amount(data: pd.Series, save_dir_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(
        data.index,
        data / 1e6,
        color=sns.color_palette("Greens_d", n_colors=len(data))[::-1],
    )
    ax.bar_label(bars, fmt="$%.1f млн.", padding=4, fontsize=9)
    ax.set_xlabel("Выручка (млн. $)")
    ax.set_ylabel("Услуга")
    ax.set_title("Выручка по услугам")
    fig.tight_layout()
    file_path = save_dir_path / "services_by_transaction_amount.png"
    fig.savefig(file_path)
    plt.close(fig)
    return file_path


def plot_client_net_worth_category_total_amount(
    data: pd.Series, save_dir_path: Path
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.bar(
        data.index,
        data / 1e6,
        color=sns.color_palette("Blues_d", n_colors=len(data))[::-1],
    )
    ax.bar_label(bars, fmt="$%.1f млн.", padding=4)
    ax.set_xlabel("Категория активов")
    ax.set_ylabel("Сумма транзакций (млн. $)")
    ax.set_title("Выручка по категориям клиентов")
    fig.tight_layout()
    file_path = save_dir_path / "client_net_worth_category_total_amount.png"
    fig.savefig(file_path)
    plt.close(fig)
    return file_path


def plot_avg_transaction_by_age(data: pd.Series, save_dir_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(11, 5))
    smoothed = pd.Series(
        data.sort_index().rolling(3, min_periods=1, center=True).mean()
    )
    ax.plot(smoothed.index, smoothed / 1_000, color="orange", linewidth=2)
    ax.scatter(data.index, data / 1_000, color="orange", alpha=0.4, s=20)
    ax.set_xlabel("Возраст клиента")
    ax.set_ylabel("Средняя сумма транзакции (тыс. $)")
    ax.set_title("Средняя сумма транзакции по возрасту клиента")
    fig.tight_layout()
    file_path = save_dir_path / "avg_transaction_amount_by_client_age.png"
    fig.savefig(file_path)
    plt.close(fig)
    return file_path


def plot_last_month_amount_by_service(data: pd.Series, save_dir_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(
        data.index,
        data / 1e6,
        color=sns.color_palette("Reds_d", n_colors=len(data))[::-1],
    )
    ax.bar_label(bars, fmt="$%.1f млн.", padding=4, fontsize=9)
    ax.set_xlabel("Выручка (млн. $)")
    ax.set_ylabel("Услуга")
    ax.set_title("Выручка по услугам за последний месяц")
    fig.tight_layout()
    file_path = save_dir_path / "last_month_amount_by_service.png"
    fig.savefig(file_path)
    plt.close(fig)
    return file_path


def plot_amount_distribution(data: pd.Series, save_dir_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(data / 1e3, bins=40, kde=True, color="lightgreen", ax=ax)
    ax.set_xlabel("Сумма транзакции (тыс. $)")
    ax.set_ylabel("Количество транзакций")
    ax.set_title("Распределение сумм транзакций")
    fig.tight_layout()
    file_path = save_dir_path / "amount_distribution.png"
    fig.savefig(file_path)
    plt.close(fig)
    return file_path


def plot_forecast(df: pd.DataFrame, preds: dict, save_dir_path: Path) -> Path:
    monthly_df = (
        df.set_index("transaction_date")
        .resample("ME")
        .agg(
            count=("amount", "count"),
            amount=("amount", "sum"),
        )
        .reset_index()
    )
    next_month = monthly_df["transaction_date"].max() + pd.DateOffset(months=1)
    all_dates = list(monthly_df["transaction_date"]) + [next_month]

    fig, axes = plt.subplots(1, 2, figsize=(8, 5))
    for ax, target, label in zip(
        axes,
        ["count", "amount"],
        ["Количество транзакций", "Выручка (млн. $)"],
    ):
        scale = 1e6 if target == "amount" else 1
        y = monthly_df[target] / scale
        pred = preds[target] / scale
        ax.bar(monthly_df["transaction_date"], y, width=20, color="skyblue")
        ax.bar([next_month], [pred], color="red", width=20, label="Прогноз")
        ax.set_title(label)
        ax.set_xticks(all_dates)
        ax.set_xticklabels(
            [d.strftime("%b %Y") for d in all_dates], fontsize=8, ha="center"
        )
        ax.legend(fontsize=8)
        fig.autofmt_xdate()

    fig.suptitle("Прогноз на следующий месяц")
    fig.tight_layout()
    file_path = save_dir_path / "forecast_next_month.png"
    fig.savefig(file_path)
    plt.close(fig)
    return file_path


def plot_analysis(
    analysis_results: dict, df: pd.DataFrame, save_dir_path: Path
) -> dict[str, Path]:
    return {
        "services_by_transaction_amount": plot_services_by_transaction_amount(
            analysis_results["services_by_transaction_amount"], save_dir_path
        ),
        "client_net_worth_category_total_amount": plot_client_net_worth_category_total_amount(
            analysis_results["client_net_worth_category_total_amount"],
            save_dir_path,
        ),
        "payment_method_pie": plot_payment_method_pie(
            analysis_results["payment_method_percentage"], save_dir_path
        ),
        "avg_transaction_amount_by_client_age": plot_avg_transaction_by_age(
            analysis_results["avg_transaction_amount_by_client_age"], save_dir_path
        ),
        "last_month_amount_by_service": plot_last_month_amount_by_service(
            analysis_results["last_month_amount_by_service"], save_dir_path
        ),
        "amount_distribution": plot_amount_distribution(
            pd.Series(df["amount"]), save_dir_path
        ),
        "forecast_next_month": plot_forecast(
            df, analysis_results["forecast_next_month"], save_dir_path
        ),
    }
