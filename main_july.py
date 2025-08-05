from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

from core.fetch_funding import fetch_funding_transactions_for_user
from filter_data_july import filter_fundings_july # Import the new function
from core.filter_sender import filter_sender_name
from core.export import export_to_csv, export_failed_to_csv
import config


def process_user_funding(user: str, api_key: str, api_secret: str) -> tuple[list, list]:

    print(f"\nProcessing user: {user}")

    if not api_key or not api_secret:
        print(f"Missing credentials for {user}. Skipping...")
        return [], []

    fundings = fetch_funding_transactions_for_user(user, api_key, api_secret)
    filtered = filter_fundings_july(fundings) # Use the new July filter

    export_to_csv(filtered, filename=f'bitso_deposits_{user}_july.csv')
    export_failed_to_csv(fundings, filename=f'bitso_failed_deposits_{user}_july.csv')

    return filtered, fundings


def generate_growth_chart(all_fundings: list, filename: str = 'bitso_july_income.png'):
    """
    Generates and saves a bar chart of daily income for July.

    Args:
        all_fundings (list): A list of all funding transaction dictionaries.
        filename (str): The name of the file to save the chart to.
    """
    print(f"\nGenerating daily income bar chart for July...")

    if not all_fundings:
        print("No funding data available to generate a bar chart.")
        return

    # Filter for successful/completed transactions only
    successful_fundings = [f for f in all_fundings if f.get('status') == 'complete']

    if not successful_fundings:
        print("No successful funding data found to generate a bar chart.")
        return

    df = pd.DataFrame(successful_fundings)

    # Convert data types for processing
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['amount'] = pd.to_numeric(df['amount'])

    # Filter for transactions in July of the current year
    now = datetime.now()
    july_df = df[(df['created_at'].dt.year == now.year) &
                       (df['created_at'].dt.month == 7)]

    if july_df.empty:
        print("No income data found for July. Bar chart not generated.")
        return

    # Group by day and sum the amounts.
    july_df.set_index('created_at', inplace=True)
    daily_income = july_df['amount'].resample('D').sum()

    # Create and style the bar chart
    plt.figure(figsize=(12, 7))
    daily_income.plot(kind='bar', color='skyblue', edgecolor='black')

    # Improve formatting
    plt.title(f'Feria lavada: July {now.year}', fontsize=16, fontweight='bold')
    plt.xlabel('Dia del mes', fontsize=12)
    plt.ylabel('Dinero para la pension', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    # Format x-axis to show only the day number
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%d'))
    plt.xticks(rotation=0)
    plt.tight_layout()

    # Save the chart to a file
    plt.savefig(filename)
    print(f"Success! Daily income bar chart saved to {filename}")
    plt.close()


def main():
    combined_data = []
    all_fundings_data = []

    for user, (api_key, api_secret) in config.API_KEYS.items():
        user_data, all_fundings = process_user_funding(user, api_key, api_secret)
        combined_data.extend(user_data)
        all_fundings_data.extend(all_fundings)

    if combined_data:
        print("\nGenerating combined summary for all accounts for July...")
        filter_sender_name(combined_data, filename='bitso_sum_by_sender_name_all_july.csv')
    else:
        print("\nNo data found for any user for July.")

    if all_fundings_data:
        print("\nGenerating combined summary of failed deposits for all accounts for July...")
        export_failed_to_csv(all_fundings_data, filename='bitso_failed_deposits_all_july.csv')
        
        # Generate the growth chart from all funding data
        generate_growth_chart(all_fundings_data)


if __name__ == '__main__':
    main()