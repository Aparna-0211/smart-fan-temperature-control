import argparse
import csv
import os
import re
import threading
import time
from datetime import datetime

import serial
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

latest = {
    "temperature": None,
    "humidity": None,
    "fan": "UNKNOWN",
    "raw": "Waiting for ESP32 serial data...",
    "timestamp": None,
    "connected": False,
    "port": None,
}

lock = threading.Lock()
stop_event = threading.Event()
ser = None

LINE_PATTERN = re.compile(
    r"Temp:\s*([0-9.+-]+)\s*C\s+Humidity:\s*([0-9.+-]+)\s*%\s+Fan:\s*(ON|OFF)",
    re.IGNORECASE,
)


def save_csv(temp, humidity, fan):
    """Save each valid reading to readings.csv for later analysis."""
    file_exists = os.path.exists("readings.csv")
    with open("readings.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "temperature_c", "humidity_percent", "fan"])
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            temp,
            humidity,
            fan,
        ])


def serial_worker(port, baud):
    global ser

    while not stop_event.is_set():
        try:
            print(f"[SERIAL] Trying {port} at {baud} baud...")
            ser = serial.Serial(port, baud, timeout=1)

            with lock:
                latest["connected"] = True
                latest["port"] = port

            print(f"[SERIAL] Connected to {port}")
            print("[SERIAL] Waiting for ESP32 data...\n")

            while not stop_event.is_set():
                line = ser.readline().decode("utf-8", errors="ignore").strip()

                if not line:
                    continue

                print(f"[ESP32] {line}")

                match = LINE_PATTERN.search(line)
                if match:
                    temp = float(match.group(1))
                    humidity = float(match.group(2))
                    fan = match.group(3).upper()

                    with lock:
                        latest.update({
                            "temperature": temp,
                            "humidity": humidity,
                            "fan": fan,
                            "raw": line,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        })

                    try:
                        save_csv(temp, humidity, fan)
                    except OSError as e:
                        print(f"[CSV] Could not save reading: {e}")

        except (serial.SerialException, OSError) as e:
            with lock:
                latest["connected"] = False

            print(f"[SERIAL] Not connected: {e}")
            print("[SERIAL] Retrying in 3 seconds...\n")
            time.sleep(3)

        finally:
            if ser is not None:
                try:
                    ser.close()
                except Exception:
                    pass
                ser = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    with lock:
        return jsonify(dict(latest))


@app.route("/api/update", methods=["POST"])
def api_update():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "No data received"}), 400

    with lock:
        if "temperature" in data:
            latest["temperature"] = data["temperature"]

        if "humidity" in data:
            latest["humidity"] = data["humidity"]

        if "fan" in data:
            latest["fan"] = data["fan"]

    return jsonify({"status": "updated"})


def main():
    parser = argparse.ArgumentParser(description="ESP32 Fan Monitoring Dashboard")
    parser.add_argument("--port", default=os.getenv("SERIAL_PORT", "COM5"),
                        help="ESP32 serial port, e.g. COM5")
    parser.add_argument("--baud", type=int, default=115200,
                        help="Serial baud rate")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--web-port", type=int, default=int(os.getenv("PORT", 5000)))
    args = parser.parse_args()

    worker = threading.Thread(
        target=serial_worker,
        args=(args.port, args.baud),
        daemon=True,
    )
    worker.start()

    print("=" * 60)
    print("ESP32 TEMPERATURE + FAN MONITOR")
    print("=" * 60)
    print(f"Serial port : {args.port}")
    print(f"Baud rate   : {args.baud}")
    print(f"Dashboard   : http://127.0.0.1:{args.web_port}")
    print("Press CTRL+C to stop.")
    print("=" * 60)

    try:
        app.run(host=args.host, port=args.web_port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        print("\nDashboard stopped.")


if __name__ == "__main__":
    main()
