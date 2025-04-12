import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, Optional

import requests
from requests.exceptions import RequestException


@dataclass
class HealthCheckConfig:
    endpoint: str = os.environ.get("HEALTH_ENDPOINT", "http://localhost:8000/health")
    check_interval: int = int(os.environ.get("CHECK_INTERVAL", "60"))
    response_threshold: float = float(os.environ.get("RESPONSE_THRESHOLD", "3.0"))
    retry_count: int = int(os.environ.get("RETRY_COUNT", "3"))
    retry_delay: float = float(os.environ.get("RETRY_DELAY", "2.0"))


@dataclass
class HealthCheckResult:
    timestamp: float
    response_time: float
    status_code: int
    is_healthy: bool
    system_stats: Optional[Dict[str, float]] = None
    error_message: Optional[str] = None


class HealthChecker:
    def __init__(self, config: HealthCheckConfig):
        self.config = config
        self.setup_logging()
        self.session = requests.Session()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(), logging.FileHandler("health_check.log")],
        )
        self.logger = logging.getLogger(__name__)

    def send_alert(self, message: str, level: str = "warning"):
        """
        Send alerts through configured channels (e.g., email, Slack, etc.)
        """
        getattr(self.logger, level)(f"ALERT: {message}")
        # Add actual alert implementation here (e.g., Slack webhook, email)

    def check_health(self) -> HealthCheckResult:
        try:
            start_time = time.perf_counter()
            response = self.session.get(
                self.config.endpoint, timeout=self.config.response_threshold + 1
            )
            response_time = time.perf_counter() - start_time

            result = HealthCheckResult(
                timestamp=time.time(),
                response_time=response_time,
                status_code=response.status_code,
                is_healthy=True,
            )

            # Check response time threshold
            if response_time > self.config.response_threshold:
                result.is_healthy = False
                result.error_message = (
                    f"Response time ({response_time:.2f}s) exceeds threshold"
                )
                self.send_alert(result.error_message)

            # Check HTTP status
            if response.status_code != 200:
                result.is_healthy = False
                result.error_message = f"Unhealthy status code: {response.status_code}"
                self.send_alert(result.error_message, "error")

            # Parse and check health data
            try:
                health_data = response.json()
                result.system_stats = health_data.get("system_stats")

                if health_data.get("db_status", "").lower() != "ok":
                    result.is_healthy = False
                    result.error_message = "Database health check failed"
                    self.send_alert(result.error_message, "error")

                # Alert on high resource usage
                if result.system_stats:
                    if result.system_stats.get("cpu_percent", 0) > 90:
                        self.send_alert("High CPU usage detected")
                    if result.system_stats.get("memory_percent", 0) > 90:
                        self.send_alert("High memory usage detected")
                    if result.system_stats.get("disk_usage", 0) > 90:
                        self.send_alert("High disk usage detected")

            except json.JSONDecodeError:
                self.logger.warning("Invalid JSON response from health endpoint")

            return result

        except RequestException as e:
            return HealthCheckResult(
                timestamp=time.time(),
                response_time=-1,
                status_code=-1,
                is_healthy=False,
                error_message=str(e),
            )

    def run(self):
        self.logger.info(f"Starting health checker for {self.config.endpoint}")

        while True:
            for attempt in range(self.config.retry_count):
                try:
                    result = self.check_health()

                    if result.is_healthy:
                        self.logger.info(
                            f"Health check passed - Response Time: {result.response_time:.2f}s, "
                            f"Status: {result.status_code}"
                        )
                        break
                    else:
                        self.logger.warning(
                            f"Health check failed - {result.error_message}"
                        )

                except Exception as e:
                    self.logger.error(f"Health check error: {e}")
                    if attempt < self.config.retry_count - 1:
                        time.sleep(self.config.retry_delay)
                    else:
                        self.send_alert(
                            f"Health check failed after {self.config.retry_count} attempts",
                            "error",
                        )

            time.sleep(self.config.check_interval)


if __name__ == "__main__":
    config = HealthCheckConfig()
    checker = HealthChecker(config)
    checker.run()
