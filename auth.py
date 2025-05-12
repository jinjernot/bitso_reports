import hmac
import hashlib
import time
from config import API_KEY, API_SECRET

def generate_auth_headers(endpoint, method='GET', query_params=None):
    nonce = str(int(time.time() * 1000))

    # Sort and build query string
    query_string = ''
    if query_params:
        sorted_params = sorted(query_params.items())
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        endpoint_with_query = f"{endpoint}?{query_string}"
    else:
        endpoint_with_query = endpoint

    message = nonce + method + endpoint_with_query
    signature = hmac.new(
        API_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return {
        'Authorization': f'Bitso {API_KEY}:{nonce}:{signature}',
        'Content-Type': 'application/json'
    }
