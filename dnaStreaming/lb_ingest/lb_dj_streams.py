from dnaStreaming.listener import Listener
from google.auth.transport.requests import Request
from google.auth import default as google_auth_default
from google.oauth2 import id_token
from datetime import datetime, timedelta
from threading import Lock
import requests
import os

listener = Listener()
print("\n[ACTIVITY] Receiving messages (SYNC)...\n[0]", end='')

# The Cloud Run service URL
service_url = os.getenv("TASK_ENGINE_URL","https://task-engine-h27ox7lv7q-uw.a.run.app")
# Obtain an OIDC token set GOOGLE_APPLICATION_CREDENTIALS in run env
creds, _ = google_auth_default()

class TokenCache:
    def __init__(self):
        self.token = None
        self.expiry = datetime.utcnow() - timedelta(minutes=1)
        self.lock = Lock()

    def get_token(self, service_url):
        with self.lock:
            # Check if the current token is expired or close to expiring
            if self.token is None or datetime.utcnow() >= self.expiry:
                # Refresh the token
                print("Refreshing token...")
                creds, _ = google_auth_default()
                self.token = id_token.fetch_id_token(Request(), service_url)
                # Assuming the token is valid for 1 hour; adjust based on actual token lifetime
                self.expiry = datetime.utcnow() + timedelta(hours=1) - timedelta(minutes=5)
        return self.token

token_cache = TokenCach()


def get_auth_header(service_url):
    try:
        oidc_token = token_cache.get_token(service_url)
        return {"Authorization": f"Bearer {oidc_token}"}
    except Exception as e:
        print(f"Failed to obtain OIDC token: {e}")
        return None


def callback(message, subscription_id):
    callback.counter += 1
    data = {
            'ingest': 'dj-streams',
            'json': message,
            'sub_collector': subscription_id,
    }
    headers = get_auth_header(service_url);

    try:
        response = requests.post(service_url, headers=headers, json=data)
        if response.status_code == 200:
            print("Message successfully sent to task-handler.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}")

        return True
    except Exception as e:
        print(f"Error sending message: {e}")
        return False


callback.counter = 0
listener.listen(callback)
