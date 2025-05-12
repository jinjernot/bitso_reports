from datetime import datetime, date, timedelta
import pandas as pd
import requests
import pytz

from auth import generate_auth_headers_for_user
from core.export import export_to_csv
import config  # <-- use this to access API_KEYS and secrets

def fetch_funding_transactions_for_user(user, api_key, api_secret):
    endpoint = '/v3/fundings'
    url = config.BASE_URL + endpoint

    all_fundings = []
    marker = None
    page_number = 1

    while True:
        params = {'limit': 100}
        if marker:
            params['marker'] = marker
            print(f"Fetching page {page_number} for {user} with marker (fid): {marker}")
        else:
            print(f"Fetching page {page_number} for {user}")

        # Generate headers with per-user credentials
        headers = generate_auth_headers_for_user(endpoint, method='GET', query_params=params,
                                                 api_key=api_key, api_secret=api_secret)

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Error fetching funding transactions for {user}: {response.text}")

        result = response.json()
        fundings = result.get('payload', [])
        if not fundings:
            print(f"No more fundings found for {user}. Breaking out of loop.")
            break

        # --- Save raw page (DISABLED for now) ---
        # raw_page_filename = f'bitso_raw_fundings_page_{user}_{page_number}.json'
        # with open(raw_page_filename, 'w') as f:
        #     json.dump(result, f, indent=4)
        # print(f"Page {page_number} response for {user} saved to {raw_page_filename}")

        all_fundings.extend(fundings)

        if len(fundings) < 100:
            print(f"Final page reached for {user} (fewer than 100 results).")
            break

        marker = fundings[-1]['fid']
        page_number += 1

    # --- Save full raw response (DISABLED for now) ---
    # save_raw_response(all_fundings, filename=f'bitso_raw_fundings_{user}.json')
    return all_fundings

# --- Save function (also disabled by commenting) ---
def save_raw_response(data, filename='bitso_raw_fundings.json'):
    # with open(filename, 'w') as f:
    #     json.dump(data, f, indent=4)
    # print(f"Raw API response saved to {filename}")
    pass

def filter_fundings_this_month(fundings):
    # Define Mexico City timezone
    mexico_tz = pytz.timezone('America/Mexico_City')
    today_local = datetime.now(mexico_tz).date()

    start_date = date(today_local.year, today_local.month, 1)
    end_date = today_local - pd.Timedelta(days=1)  # Up to yesterday in local time

    print(f"Filtering fundings from {start_date} to {end_date} (Mexico City time)")

    filtered = []
    for f in fundings:
        created_str = f.get('created_at')
        if not created_str:
            continue

        try:
            # Parse original UTC datetime
            created_utc = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%S+00:00").replace(tzinfo=pytz.UTC)
            # Convert to Mexico City local time
            created_local = created_utc.astimezone(mexico_tz).date()

            if start_date <= created_local <= end_date:
                filtered.append(f)
        except Exception as e:
            print(f"Skipping record with bad date format: {created_str} ({e})")

    print(f"Filtered down to {len(filtered)} funding transactions for this month")
    return filtered


def summarize_by_sender_name(fundings, filename='bitso_sum_by_sender_name.csv'):
    data = []
    for f in fundings:
        details = f.get('details', {})
        clabe = details.get('sender_clabe')
        amount = float(f.get('amount', 0))
        name = config.ACCOUNT.get(clabe, clabe)
        data.append({
            'Sender Name': name,
            'Amount': amount
        })

    df = pd.DataFrame(data)
    df = df.dropna(subset=['Sender Name'])
    summary = df.groupby('Sender Name', as_index=False).sum()
    summary = summary.sort_values(by='Amount', ascending=False)

    # Format with $ sign and thousands separator
    summary['Amount'] = summary['Amount'].apply(lambda x: f"${x:,.2f}")

    summary.to_csv(filename, index=False)
    print(f"Sum of deposits by Sender Name saved to {filename}")
if __name__ == '__main__':
    combined_data = []

    for user, (api_key, api_secret) in config.API_KEYS.items():
        print(f"\n📥 Processing user: {user}")

        if not api_key or not api_secret:
            print(f"❌ Missing credentials for {user}. Skipping...")
            continue

        fundings = fetch_funding_transactions_for_user(user, api_key, api_secret)
        filtered = filter_fundings_this_month(fundings)

        export_to_csv(filtered, filename=f'bitso_deposits_{user}.csv')
        summarize_by_sender_name(filtered, filename=f'bitso_sum_by_sender_name_{user}.csv')

        combined_data.extend(filtered)

    # Final combined summary
    print("\n📊 Generating combined summary for all accounts...")
    summarize_by_sender_name(combined_data, filename='bitso_sum_by_sender_name_all.csv')
