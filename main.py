from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

from core.fetch_funding import fetch_funding_transactions_for_user
from core.filter_data import filter_fundings_this_month
from core.filter_sender import filter_sender_name
from core.export import export_to_csv, export_failed_to_csv
import config


def process_user_funding(user: str, api_key: str, api_secret: str) -> tuple[list, list]:

    print(f"\nProcessing user: {user}")

    if not api_key or not api_secret:
        print(f"Missing credentials for {user}. Skipping...")
        return [], []

    fundings = fetch_funding_transactions_for_user(user, api_key, api_secret)
    filtered = filter_fundings_this_month(fundings)

    export_to_csv(filtered, filename=f'bitso_deposits_{user}.csv')
    export_failed_to_csv(fundings, filename=f'bitso_failed_deposits_{user}.csv')

    return filtered, fundings


def generate_growth_chart(all_fundings: list, filename: str = 'bitso_this_month_income.png'):
    """
    Generates and saves a line chart of daily income for the current month.

    Args:
        all_fundings (list): A list of all funding transaction dictionaries.
        filename (str): The name of the file to save the chart to.
    """
    print(f"\nGenerating daily income chart for this month...")

    if not all_fundings:
        print("No funding data available to generate a chart.")
        return

    # Filter for successful/completed transactions only
    successful_fundings = [f for f in all_fundings if f.get('status') == 'complete']

    if not successful_fundings:
        print("No successful funding data found to generate a chart.")
        return

    df = pd.DataFrame(successful_fundings)

    # Convert data types for processing
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['amount'] = pd.to_numeric(df['amount'])

    # Filter for transactions in the current month
    now = datetime.now()
    this_month_df = df[(df['created_at'].dt.year == now.year) &
                       (df['created_at'].dt.month == now.month)]

    if this_month_df.empty:
        print("No income data found for the current month. Chart not generated.")
        return

    # Group by day and sum the amounts.
    this_month_df.set_index('created_at', inplace=True)
    daily_income = this_month_df['amount'].resample('D').sum()

    # Create and style the line chart
    plt.figure(figsize=(12, 7))
    daily_income.plot(kind='line', marker='o', linestyle='-', color='dodgerblue')

    # Improve formatting
    plt.title(f'Daily Income for {now.strftime("%B %Y")}', fontsize=16, fontweight='bold')
    plt.xlabel('Day of the Month', fontsize=12)
    plt.ylabel('Total Funding Amount', fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    # Format x-axis to show only the day number
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))
    plt.tight_layout()

    # Save the chart to a file
    plt.savefig(filename)
    print(f"Success! Daily income chart saved to {filename}")
    plt.close()


def main():
    combined_data = []
    all_fundings_data = []

    for user, (api_key, api_secret) in config.API_KEYS.items():
        user_data, all_fundings = process_user_funding(user, api_key, api_secret)
        combined_data.extend(user_data)
        all_fundings_data.extend(all_fundings)

    if combined_data:
        print("\nGenerating combined summary for all accounts...")
        filter_sender_name(combined_data, filename='bitso_sum_by_sender_name_all.csv')
    else:
        print("\nNo data found for any user.")

    if all_fundings_data:
        print("\nGenerating combined summary of failed deposits for all accounts...")
        export_failed_to_csv(all_fundings_data, filename='bitso_failed_deposits_all.csv')
        
        # Generate the growth chart from all funding data
        generate_growth_chart(all_fundings_data)


if __name__ == '__main__':
    main()