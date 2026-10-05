#!/usr/bin/env python3
"""Optional Standalone Mock Ingestion Server.
Run this in a separate terminal if you want to inspect incoming AWS IoT telemetry payloads
in real time:
    python mock_receiver.py --port 8000
"""

import argparse
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class TelemetryHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            payload = json.loads(body.decode("utf-8"))
            device_id = payload.get("deviceId", "UNKNOWN")
            timestamp = payload.get("isoTime", "")
            telemetry = payload.get("telemetry", {})
            ground_truth = payload.get("_ground_truth", {})

            temp = telemetry.get("temperature_c")
            rh = telemetry.get("relative_humidity_pct")
            press = telemetry.get("pressure_hpa")
            gt_status = ground_truth.get("status", "NORMAL")

            status_indicator = "NORMAL"
            if "DEFECT" in gt_status:
                status_indicator = f"DEFECT DETECTED: {ground_truth.get('active_labels')}"
            elif "ANOMALY" in gt_status:
                status_indicator = f"WEATHER ANOMALY: {ground_truth.get('active_labels')}"

            print(
                f"[POST {self.path}] {device_id} @ {timestamp} | "
                f"T={temp}C, RH={rh}%, P={press}hPa | "
                f"[{status_indicator}]"
            )

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"accepted"}')

        except Exception as e:
            print(f"[Error parsing payload]: {e}")
            self.send_response(400)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default noisy access logs
        return

def main():
    parser = argparse.ArgumentParser(description="Mock Telemetry Receiver")
    parser.add_argument("--port", type=int, default=8000, help="Listening port (default 8000)")
    args = parser.parse_args()

    server_address = ("127.0.0.1", args.port)
    httpd = HTTPServer(server_address, TelemetryHandler)
    print(f"==================================================")
    print(f" Mock Telemetry Ingestion Server Running")
    print(f" Endpoint: http://127.0.0.1:{args.port}/api/telemetry")
    print(f" Press Ctrl+C to terminate")
    print(f"==================================================")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nReceiver stopped.")

if __name__ == "__main__":
    main()
