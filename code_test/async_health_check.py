import os
import asyncio
import logging
import json
import time
from aiohttp import ClientSession, ClientTimeout

# Configuration via environment variables
# Provide a comma-separated list of endpoints, e.g. "http://localhost:8000/health,http://localhost:8001/health"
HEALTH_ENDPOINTS = os.environ.get("HEALTH_ENDPOINTS", "http://localhost:8000/health").split(',')
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "300"))  # seconds
RESPONSE_THRESHOLD = float(os.environ.get("RESPONSE_THRESHOLD", "3.0"))  # seconds

# Configure logging to output timestamp, level, and message
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def fetch_health(session: ClientSession, url: str):
    try:
        start_time = time.perf_counter()
        timeout = ClientTimeout(total=RESPONSE_THRESHOLD + 1)
        async with session.get(url, timeout=timeout) as response:
            response_time = time.perf_counter() - start_time
            status = response.status
            text = await response.text()
            logging.info(f"Endpoint: {HEALTH_ENDPOINTS}, Response Time: {response_time:.2f}s, Status Code: {status}")
            
            # Optionally check Json Health Indicator for ok status
            try: 
                data = json.loads(text)
                if data.get('db_status', '').lower() != 'ok':
                    error_message = f"Database connectivity issue detected at {url}"
                    logging.error(error_message)
            except json.JSONDecodeError:
                logging.warning(f"Response from {url} is not valid JSON")
                
            # Alert if response time exceeds threshold
            if response_time > RESPONSE_THRESHOLD:
                warning_message = f"Response time {response_time:.2f}s at {url} exceeds threshold {RESPONSE_THRESHOLD}s"
                logging.warning(warning_message)
            
            if status != 200:
                error_message = f"HTTP Error at {url}: Received status code {status}"
                logging.error(error_message)
    except asyncio.TimeoutError:
        error_message = f"HTTP Error at {url}:"
        logging.error(error_message)
    except Exception as e:
        error_message = f"Request error for {url}: {e}"
        logging.error(error_message)
        
async def health_check():
    async with ClientSession() as session:
        tasks = [fetch_health(session, url.strip()) for url in HEALTH_ENDPOINTS]
        await asyncio.gather(*tasks, return_exceptions=True)

async def main_loop():
    while True:
        await health_check()
        await asyncio.sleep(CHECK_INTERVAL)
        
if __name__ == '__main__':
    asyncio.run(main_loop())