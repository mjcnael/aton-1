import os
from pathlib import Path
import pandas as pd
from datetime import datetime

from .plot_analysis import plot_analysis


def _table(data: pd.Series | pd.DataFrame, fmt: str = "{:,.0f}") -> str:
    return data.apply(lambda x: fmt.format(x)).to_markdown()


def generate_md_report(
    results: dict[str, pd.Series],
    df: pd.DataFrame,
    save_file_path: Path,
) -> str:
    plots_path = Path(save_file_path.parent / "plots")
    os.makedirs(plots_path, exist_ok=True)
    plots = plot_analysis(results, df, plots_path)

    report = f"""# Анализ финансовых транзакций
{datetime.now().strftime("%d.%m.%Y %H:%M")}

## Топ-5 услуг по количеству транзакций
{_table(results["services_by_count"].head(5))}

## Услуга с наибольшей выручкой
{_table(results["services_by_transaction_amount"].head(1), "${:,.0f}")}

## Выручка по услугам
![Services by transaction amount]({plots["services_by_transaction_amount"].relative_to(save_file_path.parent)})

Общая выручка за последний месяц: ${results["last_month_total_amount"]:,.0f}

![Last month amount by service]({plots["last_month_amount_by_service"].relative_to(save_file_path.parent)})

## Топ-5 средних сумм транзакций по городам
{_table(results["avg_transaction_amount_by_city"].head(5), "${:,.0f}")}

## Выручка по категориям клиентов
![Client net worth category total amount]({plots["client_net_worth_category_total_amount"].relative_to(save_file_path.parent)})

## Доля транзакций по способам оплаты
![Payment method]({plots["payment_method_pie"].relative_to(save_file_path.parent)})

## Средняя сумма транзакции по возрасту клиента
![Average transaction by age]({plots["avg_transaction_amount_by_client_age"].relative_to(save_file_path.parent)})

## Распределение сумм транзакций
![Amount distribution]({plots["amount_distribution"].relative_to(save_file_path.parent)})

## Прогноз на следующий месяц
Прогноз количества транзакций: {results["forecast_next_month"]["count"]}

Прогноз выручки: ${results["forecast_next_month"]["amount"]:,.0f}

![Forecast next month]({plots["forecast_next_month"].relative_to(save_file_path.parent)})
"""
    with open(save_file_path, "w", encoding="utf-8") as f:
        f.write(report)
        print(f"Report generated: {save_file_path}")
    return report
