import os
import platform
import socket
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "it_assets.db")


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT NOT NULL,
                ip_or_host TEXT NOT NULL,
                port INTEGER DEFAULT 80,
                device_type TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL
            )
        """)


def check_host_status(host, port=80, timeout=1.5):
    """Checks if a host/port is reachable over TCP (works on PC, Android, and iOS without root)."""
    try:
        with socket.create_connection((host, int(port)), timeout=timeout):
            return "Online"
    except Exception:
        return "Offline / Unreachable"


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Cross-Platform IT Asset & Network Monitor</title>
  <style>
    :root {
      --bg: #0f172a;
      --surface: #1e293b;
      --card: #334155;
      --primary: #38bdf8;
      --text: #f8fafc;
      --muted: #94a3b8;
      --online: #22c55e;
      --offline: #ef4444;
    }
    * { box-sizing: border-box; font-family: system-ui, -apple-system, sans-serif; }
    body { background: var(--bg); color: var(--text); margin: 0; padding: 16px; }
    .wrapper { max-width: 960px; margin: 0 auto; }
    header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 1px solid #334155;
    }
    header h1 { margin: 0; font-size: 1.4rem; color: var(--primary); }
    .sys-badge {
      background: var(--surface);
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 0.8rem;
      color: var(--muted);
    }
    .grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 20px;
    }
    @media (min-width: 768px) {
      .grid { grid-template-columns: 320px 1fr; }
    }
    .panel {
      background: var(--surface);
      padding: 18px;
      border-radius: 12px;
    }
    .panel h2 { margin-top: 0; font-size: 1.1rem; }
    label { display: block; font-size: 0.85rem; margin: 10px 0 4px; color: var(--muted); }
    input, select {
      width: 100%;
      padding: 10px;
      border-radius: 8px;
      border: 1px solid #475569;
      background: var(--bg);
      color: var(--text);
      font-size: 0.95rem;
    }
    button {
      margin-top: 14px;
      width: 100%;
      padding: 11px;
      border: none;
      border-radius: 8px;
      background: var(--primary);
      color: #0f172a;
      font-weight: 700;
      font-size: 0.95rem;
      cursor: pointer;
    }
    .asset-list { display: flex; flex-direction: column; gap: 12px; }
    .asset-card {
      background: var(--card);
      padding: 14px;
      border-radius: 10px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
    }
    .status {
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 0.78rem;
      font-weight: 700;
    }
    .status.Online { background: rgba(34, 197, 94, 0.2); color: var(--online); }
    .status.Offline { background: rgba(239, 68, 68, 0.2); color: var(--offline); }
    .del-link {
      color: #fca5a5;
      text-decoration: none;
      font-size: 0.82rem;
      margin-left: 10px;
    }
  </style>
</head>
<body>
  <div class="wrapper">
    <header>
      <div>
        <h1>IT Asset & Network Monitor</h1>
        <small style="color: var(--muted);">Cross-Platform Diagnostic Dashboard (PC • Android • iOS)</small>
      </div>
      <span class="sys-badge">Host OS: {{ host_os }}</span>
    </header>

    <div class="grid">
      <div class="panel">
        <h2>Add Device / Endpoint</h2>
        <form method="POST" action="/add">
          <label>Device Name</label>
          <input type="text" name="device_name" placeholder="e.g., Main Router / Office PC" required />

          <label>Host / IP Address</label>
          <input type="text" name="ip_or_host" placeholder="e.g., 8.8.8.8 or google.com" required />

          <label>TCP Port to Probe</label>
          <input type="number" name="port" value="80" min="1" max="65535" required />

          <label>Category</label>
          <select name="device_type">
            <option value="Router / Gateway">Router / Gateway</option>
            <option value="Workstation / PC">Workstation / PC</option>
            <option value="Web Server / Cloud">Web Server / Cloud</option>
            <option value="Printer / Peripheral">Printer / Peripheral</option>
          </select>

          <label>Notes</label>
          <input type="text" name="notes" placeholder="Location or serial info..." />

          <button type="submit">+ Save & Test Connection</button>
        </form>
      </div>

      <div class="panel">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <h2 style="margin:0;">Monitored Endpoints ({{ assets|length }})</h2>
          <a href="/" style="color:var(--primary); text-decoration:none; font-size:0.85rem;">↻ Refresh Checks</a>
        </div>

        {% if not assets %}
          <p style="color: var(--muted);">No endpoints added yet. Add a router IP or domain on the left.</p>
        {% endif %}

        <div class="asset-list">
          {% for item in assets %}
            <div class="asset-card">
              <div>
                <strong>{{ item.device_name }}</strong>
                <span style="color:var(--muted); font-size:0.82rem;">({{ item.device_type }})</span>
                <div style="font-size:0.85rem; color:#cbd5e1; margin-top:4px;">
                  Target: <code>{{ item.ip_or_host }}:{{ item.port }}</code>
                  {% if item.notes %} • {{ item.notes }}{% endif %}
                </div>
              </div>
              <div>
                <span class="status {{ 'Online' if item.status == 'Online' else 'Offline' }}">
                  {{ item.status }}
                </span>
                <a class="del-link" href="/delete/{{ item.id }}">Remove</a>
              </div>
            </div>
          {% endfor %}
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""


@app.route("/")
def index():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM assets ORDER BY id DESC").fetchall()

    assets = []
    for r in rows:
        item = dict(r)
        item["status"] = check_host_status(item["ip_or_host"], item["port"])
        assets.append(item)

    host_os = f"{platform.system()} ({platform.machine()})"
    return render_template_string(HTML_TEMPLATE, assets=assets, host_os=host_os)


@app.route("/add", methods=["POST"])
def add_asset():
    device_name = request.form.get("device_name", "").strip()
    ip_or_host = request.form.get("ip_or_host", "").strip()
    port = int(request.form.get("port", 80))
    device_type = request.form.get("device_type", "Workstation / PC")
    notes = request.form.get("notes", "").strip()

    if device_name and ip_or_host:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO assets (device_name, ip_or_host, port, device_type, notes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (device_name, ip_or_host, port, device_type, notes, datetime.now().strftime("%Y-%m-%d %H:%M")),
            )
    return redirect(url_for("index"))


@app.route("/delete/<int:asset_id>")
def delete_asset(asset_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    # host='0.0.0.0' allows access from a PC, Android, or iOS browser on the same Wi-Fi
    app.run(host="0.0.0.0", port=5000, debug=True)
