# cross-platform-it-dashboard
Self-hosted IT inventory and endpoint connectivity monitor using Python sockets, Flask, and SQLite. Zero OS-specific dependencies—runs on Windows, Linux, macOS, Android (Termux), and iOS.

# Cross-Platform IT Asset & Network Monitor

A lightweight Python + Flask + SQLite web dashboard for tracking IT hardware and running live TCP connectivity checks across **Windows/Linux/macOS**, **Android**, and **iOS**.

## Why It Works Everywhere
- **Zero OS-Specific Dependencies:** Uses Python's `socket` module instead of OS-specific `ping` flags, so it runs without root/admin privileges on mobile devices and desktops alike.
- **Responsive CSS Grid UI:** Automatically adapts from a single-column mobile layout (Android/iOS) to a two-column desktop dashboard (PC).
- **Local Network Sharing:** Binds to `0.0.0.0:5000`, allowing you to run the server on one device and view it from any phone or computer on the same Wi-Fi.

## How to Run

### 1. PC (Windows / Linux / macOS)
```bash
pip install flask
python app.py
