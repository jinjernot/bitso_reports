import pytz
from datetime import datetime, date
import pandas as pd
from dateutil import parser

def filter_fundings_this_month(fundings):
    mexico_tz = pytz.timezone('America/Mexico_City')
    today_local = datetime.now(mexico_tz).date()

    if today_local.day == 1:
        prev_month = today_local.replace(day=1) - pd.Timedelta(days=1)
        start_date = date(prev_month.year, prev_month.month, 1)
        end_date = prev_month
    else:
        start_date = date(today_local.year, today_local.month, 1)
        end_date = today_local - pd.Timedelta(days=1)

    print(f"Filtering fundings from {start_date} to {end_date} (Mexico City time)")

    filtered = []
    for f in fundings:
        created_str = f.get('created_at')
        if not created_str:
            continue

        try:
            created_local = parser.isoparse(created_str).astimezone(mexico_tz).date()
            #print(f"{created_str} → Local Date: {created_local}")
            if start_date <= created_local <= end_date:
                filtered.append(f)
        except Exception as e:
            print(f"Skipping record with bad date format: {created_str} ({e})")

    print(f"Filtered down to {len(filtered)} funding transactions")
    return filtered
