import time

import psutil
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health_check():
    health_data = {
        "status": "ok",
        "timestamp": time.time(),
        "system_stats": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage("/").percent,
        },
        "db_status": "ok",  # This could be replaced with actual DB connectivity check
    }
    return jsonify(health_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
