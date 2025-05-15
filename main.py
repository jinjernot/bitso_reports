from datetime import datetime
import pandas as pd

from core.fetch_funding import fetch_funding_transactions_for_user
from core.filter_data import filter_fundings_this_month
from core.filter_sender import filter_sender_name
from core.export import export_to_csv
import config


def process_user_funding(user: str, api_key: str, api_secret: str) -> list:

    print(f"\nProcessing user: {user}")

    if not api_key or not api_secret:
        print(f"Missing credentials for {user}. Skipping...")
        return []

    fundings = fetch_funding_transactions_for_user(user, api_key, api_secret)
    filtered = filter_fundings_this_month(fundings)

    export_to_csv(filtered, filename=f'bitso_deposits_{user}.csv')
    #filter_sender_name(filtered, filename=f'bitso_sum_by_sender_name_{user}.csv')

    return filtered


def main():
    combined_data = []

    for user, (api_key, api_secret) in config.API_KEYS.items():
        user_data = process_user_funding(user, api_key, api_secret)
        combined_data.extend(user_data)

    if combined_data:
        print("\nGenerating combined summary for all accounts...")
        filter_sender_name(combined_data, filename='bitso_sum_by_sender_name_all.csv')
    else:
        print("\nNo data found for any user.")


if __name__ == '__main__':
    main()
