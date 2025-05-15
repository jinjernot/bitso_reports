import pytz
from datetime import datetime, date
import pandas as pd

def filter_fundings_this_month(fundings):
    mexico_tz = pytz.timezone('America/Mexico_City')
    today_local = datetime.now(mexico_tz).date()

    start_date = date(today_local.year, today_local.month, 1)
    end_date = today_local #- pd.Timedelta(days=1)  # aqui se comenta para el dia anterior

    print(f"Filtering fundings from {start_date} to {end_date} (Mexico City time)")

    filtered = []
    for f in fundings:
        created_str = f.get('created_at')
        if not created_str:
            continue

        try:
            created_utc = datetime.strptime(created_str, "%Y-%m-%dT%H:%M:%S+00:00").replace(tzinfo=pytz.UTC)

            created_local = created_utc.astimezone(mexico_tz).date()

            if start_date <= created_local <= end_date:
                filtered.append(f)
        except Exception as e:
            print(f"Skipping record with bad date format: {created_str} ({e})")

    print(f"Filtered down to {len(filtered)} funding transactions for this month")
    return filtered

