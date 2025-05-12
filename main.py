from datetime import datetime, date
import pandas as pd
import requests
import json

from auth import generate_auth_headers
from core.export import export_to_csv
from config import *

def fetch_funding_transactions():
    endpoint = '/v3/fundings'
    url = BASE_URL + endpoint

    all_fundings = []
    marker = None
    page_number = 1

    while True:
        params = {'limit': 100}
        if marker:
            params['marker'] = marker
            print(f"Fetching page {page_number} with marker (fid): {marker}")
        else:
            print(f"Fetching page {page_number}")

        # Generate fresh headers per request with correct query params
        headers = generate_auth_headers(endpoint, method='GET', query_params=params)
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Error fetching funding transactions: {response.text}")

        result = response.json()
        fundings = result.get('payload', [])
        if not fundings:
            print("No more fundings found. Breaking out of loop.")
            break

        # Save raw page
        raw_page_filename = f'bitso_raw_fundings_page_{page_number}.json'
        with open(raw_page_filename, 'w') as f:
            json.dump(result, f, indent=4)
        print(f"Page {page_number} response saved to {raw_page_filename}")

        all_fundings.extend(fundings)

        if len(fundings) < 100:
            print("Final page reached (fewer than 100 results).")
            break

        marker = fundings[-1]['fid']
        page_number += 1

    save_raw_response(all_fundings)
    return all_fundings

def save_raw_response(data, filename='bitso_raw_fundings.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Raw API response saved to {filename}")

    
def filter_fundings_this_month(fundings):
    today = date.today()
    start_date = date(today.year, today.month, 1)
    end_date = today.replace(day=today.day - 1)

    print(f"Filtering fundings from {start_date} to {end_date}")

    filtered = []
    for f in fundings:
        created_str = f.get('created_at')
        if not created_str:
            continue

        try:
            created_date = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%S+00:00").date()
            if start_date <= created_date <= end_date:
                filtered.append(f)
        except Exception as e:
            print(f"Skipping record with bad date format: {created_str} ({e})")

    print(f"Filtered down to {len(filtered)} funding transactions for this month (up to yesterday)")
    return filtered

def summarize_by_sender_name(fundings, filename='bitso_sum_by_sender_name.csv'):

    data = []
    for f in fundings:
        details = f.get('details', {})
        clabe = details.get('sender_clabe')
        amount = float(f.get('amount', 0))
        name = ACCOUNT.get(clabe, clabe)
        data.append({
            'Sender Name': name,
            'Amount': amount
        })

    df = pd.DataFrame(data)
    df = df.dropna(subset=['Sender Name'])
    summary = df.groupby('Sender Name', as_index=False).sum()
    summary = summary.sort_values(by='Amount', ascending=False)
    summary.to_csv(filename, index=False)
    print(f"Sum of deposits by Sender Name saved to {filename}")


if __name__ == '__main__':
    fundings = fetch_funding_transactions()
    fundings = filter_fundings_this_month(fundings)
    export_to_csv(fundings)
    summarize_by_sender_name(fundings)