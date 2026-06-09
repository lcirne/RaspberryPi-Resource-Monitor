# Raspberry Pi Resource Monitor
A touchscreen dashboard for a Raspberry Pi that receives live system resource data
from other computers on the network.

<img width="835" height="487" alt="Screenshot 2026-06-09 at 12 45 53 PM" src="https://github.com/user-attachments/assets/a323c5a8-11e9-4076-a224-86631d5246ee" />

## Setup

Install Python dependencies on the Pi and each client machine:

```bash
python3 -m pip install -r requirements.txt
```

## Run The Pi Dashboard

On the Raspberry Pi:

```bash
python3 gui.py --fullscreen
```

The GUI starts the TCP server automatically on port `4000`. Press `Escape` to
leave fullscreen.

For a headless server without the touchscreen GUI:

```bash
python3 server.py
```

## Run A Client

On each laptop or desktop that should appear on the Pi:

```bash
python3 client.py <pi-ip-address>
```

Example:

```bash
python3 client.py 192.168.1.50
```

Clients reconnect automatically if the Pi server restarts or the network drops.

## Notes

- The dashboard is sized for an 800x480 7 inch Raspberry Pi touchscreen.
- Data is stored locally in `resources.db`.
- Each client sends CPU, memory, disk, and network throughput once per second.
