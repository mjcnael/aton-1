import os
import pandas as pd
from datetime import datetime

from .plot_analysis import plot_analysis


def _table(data: pd.Series | pd.DataFrame, fmt: str = "{:,.0f}") -> str:
    return data.apply(lambda x: fmt.format(x)).to_markdown()


def generate_md_report(
    results: dict[str, pd.Series],
    df: pd.DataFrame,
    save_path: str,
) -> str:
    report_dir = os.path.dirname(save_path)
    plots_path = os.path.join(report_dir, "plots")
    os.makedirs(plots_path, exist_ok=True)
    plots = plot_analysis(results, df, plots_path)

    report = f"""# Анализ финансовых транзакций
{datetime.now().strftime("%d.%m.%Y %H:%M")}

## Топ-5 услуг по количеству транзакций
{_table(results["services_by_count"].head(5))}

## Услуга с наибольшей выручкой
{_table(results["services_by_transaction_amount"].head(1), "${:,.0f}")}

## Выручка по услугам
![Services by transaction amount]({os.path.relpath(plots["services_by_transaction_amount"], report_dir)})

Общая выручка за последний месяц: ${results["last_month_total_amount"]:,.0f}

![Last month amount by service]({os.path.relpath(plots["last_month_amount_by_service"], report_dir)})

## Топ-5 средних сумм транзакций по городам
{_table(results["avg_transaction_amount_by_city"].head(5), "${:,.0f}")}

## Выручка по категориям клиентов
![Client net worth category total amount]({os.path.relpath(plots["client_net_worth_category_total_amount"], report_dir)})

## Доля транзакций по способам оплаты
![Payment method]({os.path.relpath(plots["payment_method_pie"], report_dir)})

## Средняя сумма транзакции по возрасту клиента
![Average transaction by age]({os.path.relpath(plots["avg_transaction_amount_by_client_age"], report_dir)})

## Распределение сумм транзакций
![Amount distribution]({os.path.relpath(plots["amount_distribution"], report_dir)})

## Прогноз на следующий месяц
Прогноз количества транзакций: {results["forecast_next_month"]["count"]}

Прогноз выручки: ${results["forecast_next_month"]["amount"]:,.0f}

![Forecast next month]({os.path.relpath(plots["forecast_next_month"], report_dir)})
"""
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(report)
        print(f"Report generated: {save_path}")
    return report
