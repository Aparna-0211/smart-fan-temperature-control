# ESP32 Smart Fan Local Dashboard

This project connects an ESP32 running your Arduino IDE code to a Python/Flask website.

## Data flow

DHT11 → ESP32 → `Serial.printf()` → USB Serial → Python/PySerial → Flask → Browser Dashboard

The Python program also prints the ESP32 serial output in CMD and saves valid readings to `readings.csv`.

## 1. Arduino IDE

Upload your existing ESP32 code.

Your code already sends lines like:

```text
Temp: 32.4 C  Humidity: 65 %  Fan: OFF
```

The Python dashboard reads exactly this format.

### Important

Do **not** keep Arduino IDE Serial Monitor open while the Python program is reading the same COM port. Usually only one program can use the serial port at a time.

## 2. Find the ESP32 COM port

In Arduino IDE:

**Tools → Port**

Example:

```text
COM5
```

Use the actual port shown on your computer.

## 3. Install Python packages

Open CMD inside this folder:

```bat
py -m pip install -r requirements.txt
```

If `py` does not work:

```bat
python -m pip install -r requirements.txt
```

## 4. Start the dashboard

Example for COM5:

```bat
py app.py --port COM5
```

Then open:

```text
http://127.0.0.1:5000
```

or:

```text
http://localhost:5000
```

The CMD window will show:

```text
ESP32 TEMPERATURE + FAN MONITOR
============================================================
Serial port : COM5
Baud rate   : 115200
Dashboard   : http://127.0.0.1:5000
============================================================
[ESP32] Temp: 32.4 C  Humidity: 65 %  Fan: OFF
```

## 5. If your port changes

Just run:

```bat
py app.py --port COM6
```

You can also use an environment variable:

```bat
set SERIAL_PORT=COM5
py app.py
```

## 6. What the dashboard shows

- Live temperature
- Live humidity
- Fan ON/OFF
- ESP32 connection status
- COM port
- Last update time
- Raw serial line
- Your ON/OFF thresholds
- Minimum fan ON time

The browser refreshes the data every second without refreshing the page.

## 7. CSV logging

Every valid sensor reading is automatically added to:

```text
readings.csv
```

This can later be opened in Excel or used for graphs/data analysis.

## 8. GitHub

Create a GitHub repository, then from this project folder:

```bat
git init
git add .
git commit -m "Initial ESP32 smart fan monitoring dashboard"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Do not upload private credentials or API keys.

## Project structure

```text
fan_monitor_dashboard/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── run_dashboard.bat
│
├── templates/
│   └── index.html
│
└── static/
    └── style.css
```
