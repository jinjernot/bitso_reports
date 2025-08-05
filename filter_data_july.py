import pytz
from datetime import datetime, date
import pandas as pd
from dateutil import parser

def filter_fundings_july(fundings):
    mexico_tz = pytz.timezone('America/Mexico_City')
    
    # We are in August 2025, so we need to get data for July 2025
    current_year = 2025
    start_date = date(current_year, 7, 1)
    end_date = date(current_year, 7, 31)

    print(f"Filtering fundings from {start_date} to {end_date} (Mexico City time)")

    filtered = []
    for f in fundings:
        created_str = f.get('created_at')
        if not created_str:
            continue

        try:
            created_local = parser.isoparse(created_str).astimezone(mexico_tz).date()
            if start_date <= created_local <= end_date:
                filtered.append(f)
        except Exception as e:
            print(f"Skipping record with bad date format: {created_str} ({e})")

    print(f"Filtered down to {len(filtered)} funding transactions")
    return filtered