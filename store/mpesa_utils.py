import base64
from datetime import datetime
import requests
from django.conf import settings
# M-Pesa utility functions for generating timestamps and passwords, and fetching access tokens
def generate_timestamp():
    return datetime.now().strftime('%Y%m%d%H%M%S')

def generate_password(shortcode, passkey, timestamp):
    data = shortcode + passkey + timestamp
    return base64.b64encode(data.encode()).decode()

def get_mpesa_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    print("M-Pesa Token Response:", r.text)  # Log the full response
    data = r.json()
    token = data.get('access_token')
    print("M-Pesa Access Token:", token)      # Log the token
    return token