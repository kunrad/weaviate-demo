import os
import time
import logging
import requests
import json
from requests.exceptions import RequestException

# Configuration via environment variables with defaults
HEALTH_ENDPOINT = os.environ.get('HEALTH_ENDPOINT', 'http://localhost:8000/health')
CHECK_INTERVAL = int(os.environ.get('CHECK_INTERVAL', 100))  # in seconds (default: 5 minutes)
RESPONSE_THRESHOLD = float(os.environ.get('RESPONSE_THRESHOLD', 3.0))  # in seconds
RETRY_COUNT = int(os.environ.get('RETRY_COUNT', 3))
RETRY_DELAY = float(os.environ.get('RETRY_DELAY', 2.0))  # seconds between retries

# Configure logging to output timestamp, level, and message
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_alert(message):
    """
    Simulate sending an alert (e.g., email or Slack).
    In a production system, replace this with an actual notification service.
    """
    logging.info(f"ALERT: {message}")
        
def check_health_check(response, response_time):
    """
    Perform a single health check request.
    Measures response time, checks HTTP status, and optionally inspects JSON health indicators.
    """
    
    try:
        start_time = time.perf_counter()
        response = requests.get(HEALTH_ENDPOINT, timeout=RESPONSE_THRESHOLD + 1)
        response_time = time.perf_counter() - start_time

        # Log basic health check info
        logging.info(f"Endpoint: {HEALTH_ENDPOINT}, Response Time: {response_time:.2f}s, Status Code: {response.status_code}")

        # Check if the response time exceeds the threshold
        if response_time > RESPONSE_THRESHOLD:
            warning_message = f"Response time {response_time:.2f}s exceeds threshold of {RESPONSE_THRESHOLD}s"
            logging.warning(warning_message)
            send_alert(warning_message)

        # Check if the HTTP status code indicates an error
        if response.status_code != 200:
            error_message = f"HTTP Error: Received status code {response.status_code}"
            logging.error(error_message)
            send_alert(error_message)

        # Optionally, inspect the response body if JSON is returned
        try:
            health_data = response.json()
            # Example: Check a 'db_status' field in the JSON response
            if 'db_status' in health_data and health_data['db_status'].lower() != 'ok':
                error_message = "Database connectivity issue detected in health check"
                logging.error(error_message)
                send_alert(error_message)
        except json.JSONDecodeError:
            # Response was not JSON formatted; skip parsing.
            pass

    except RequestException as e:
        error_message = f"Request failed: {e}"
        logging.error(error_message)
        send_alert(error_message)

def perform_health_check(session):
    """
    Perform a single health check request and evaluate the response
    """
    try:
        start_time = time.perf_counter()
        response = session.get(HEALTH_ENDPOINT, timeout=RESPONSE_THRESHOLD + 1)
        response_time = time.perf_counter() - start_time
        check_health_check(response, response_time)
    except RequestException as e:
        error_message = f"Request failed: {e}"
        logging.error(error_message)
        send_alert(error_message)
        
def health_check_loop():
    """
    Runs the health check repeatedly at the configured interval.
    Implements a retry mechanism for transient failures.
    """
    with requests.Session() as session:
        while True:
            for attempt in range(1, RETRY_COUNT + 1):
                try:
                    perform_health_check(session)
                    break  # Exit retry loop if successful
                except Exception as e:
                    logging.error(f"Attempt {attempt}/{RETRY_COUNT} failed: {e}")
                    if attempt < RETRY_COUNT:
                        time.sleep(RETRY_DELAY)
                    else:
                        send_alert(f"Health check failed after {RETRY_COUNT} attempts")
            time.sleep(CHECK_INTERVAL)
                    
if __name__ == '__main__':
    health_check_loop()
