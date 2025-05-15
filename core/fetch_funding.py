

from auth import generate_auth_headers_for_user

import requests
import config

def save_raw_response(data, filename='bitso_raw_fundings.json'):
    # with open(filename, 'w') as f:
    #     json.dump(data, f, indent=4)
    # print(f"Raw API response saved to {filename}")
    pass

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

    # save_raw_response(all_fundings, filename=f'bitso_raw_fundings_{user}.json')
    return all_fundings