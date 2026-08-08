# 🖥️ Proxmox Monitor

**Lightweight, real-time Proxmox and Linux server monitoring with Discord notifications.**

Proxmox Monitor is a lightweight Python-based monitoring service designed for **Proxmox VE hosts, Linux servers, and homelab infrastructure**.

It continuously monitors critical system resources, detects infrastructure events, performs periodic Internet speed tests, generates daily health reports, and delivers actionable notifications directly to Discord.

Designed with simplicity and reliability in mind, Proxmox Monitor can run directly on a Proxmox host or any compatible Linux system.

---

## ✨ Features

### 📊 System Monitoring

Proxmox Monitor continuously tracks:

* ⚙️ CPU utilization
* 🧠 RAM utilization
* 💾 Disk utilization
* 🌡️ System temperature
* 🔋 Battery level
* 🔌 AC / charger state
* 🌐 Internet connectivity

The default monitoring interval is **10 seconds**.

---

### 🚨 Discord Notifications

Important system events are automatically delivered to a configured Discord channel using clean Discord embeds.

Supported notifications include:

* 🔴 High CPU utilization
* 🔴 High RAM utilization
* 🔴 High disk utilization
* 🌡️ Critical system temperature
* 🔋 Low battery
* 🔌 Charger connected
* 🔌 Charger disconnected
* 🌐 Internet connection restored
* 🟢 Monitor startup notification

Notifications include timestamps and relevant system information to make incidents easy to identify.

A cooldown mechanism prevents repeated alerts when a critical condition remains active.

---

## 🌐 Internet Connectivity Monitoring

The monitor continuously checks Internet connectivity using a public DNS endpoint.

It detects:

* Internet connection loss
* Internet connection recovery
* Current online/offline state

When connectivity is restored, the monitor automatically sends an **Internet Restored** notification.

> **Note:** If the Internet connection is completely unavailable, Discord notifications cannot be delivered until connectivity returns.

---

## 📡 Internet Speed Monitoring

Internet performance is measured automatically every **15 minutes** by default.

Each speed test records:

| Metric      | Description            |
| ----------- | ---------------------- |
| ⬇️ Download | Download bandwidth     |
| ⬆️ Upload   | Upload bandwidth       |
| 📶 Ping     | Network latency        |
| 🌍 Server   | Speed-test server used |

The latest speed-test results are displayed in:

* `/status`
* Daily reports

> Speed tests generate additional network traffic. Adjust `SPEEDTEST_INTERVAL` if required.

---

## 📅 Daily Server Reports

Proxmox Monitor can generate a daily server health report containing the latest available metrics.

Example report data:

| Metric          | Information                |
| --------------- | -------------------------- |
| ⚙️ CPU          | Current CPU utilization    |
| 🧠 RAM          | Current memory utilization |
| 💾 Disk         | Current disk utilization   |
| 🌡️ Temperature | Current system temperature |
| 🔋 Battery      | Current battery percentage |
| 🔌 Charger      | AC / charger state         |
| 🌐 Internet     | Online / Offline           |
| ⬇️ Download     | Latest download speed      |
| ⬆️ Upload       | Latest upload speed        |
| 📶 Ping         | Latest latency             |

Daily reporting is configured for a maximum retention period of **30 days**.

---

## `/status` Command

The Discord slash command:

```text
/status
```

returns the current server health.

Example:

```text
🖥️ PROXMOX SERVER STATUS

⚙️ CPU          23.4%
🧠 RAM          41.2%
💾 Disk         58.7%
🌡️ Temperature  47.0°C
🔋 Battery      82%
🔌 Charger      🟢 Connected
🌐 Internet     🟢 Online

⬇️ Download     245.8 Mbps
⬆️ Upload       94.2 Mbps
📶 Ping          8 ms
```

This provides a quick way to check server health directly from Discord without accessing the Proxmox console.

---

# 🏗️ Architecture

```text
┌─────────────────────────────────────┐
│           Proxmox / Linux           │
│                                     │
│  ┌───────────────────────────────┐  │
│  │       Proxmox Monitor         │  │
│  │            Python             │  │
│  └───────────────┬───────────────┘  │
│                  │                  │
│       ┌──────────┴──────────┐       │
│       │                     │       │
│  System Metrics        Network       │
│       │                     │       │
│  ┌────┴────────┐      ┌─────┴────┐ │
│  │ CPU         │      │ Internet  │ │
│  │ RAM         │      │ Speedtest │ │
│  │ Disk        │      │ Ping      │ │
│  │ Temperature │      └───────────┘ │
│  │ Battery     │                    │
│  │ AC Power    │                    │
│  └─────────────┘                    │
└──────────────────┬──────────────────┘
                   │
                   │ Discord API
                   ▼
        ┌────────────────────────┐
        │     Discord Channel    │
        │                        │
        │ 🚨 Alerts              │
        │ 📊 Daily Reports       │
        │ 🖥️ /status             │
        └────────────────────────┘
```

---

# 🛠️ Technology Stack

| Technology        | Purpose                        |
| ----------------- | ------------------------------ |
| **Python 3**      | Core application               |
| **psutil**        | System and hardware statistics |
| **discord.py**    | Discord bot and slash commands |
| **speedtest**     | Internet performance testing   |
| **python-dotenv** | Environment configuration      |
| **asyncio**       | Asynchronous monitoring loops  |

---

# 📋 Requirements

Before installation, ensure the following requirements are available:

* Linux-based operating system
* Python 3.x
* Internet connectivity
* Discord application and bot
* Discord channel ID
* Required Discord bot permissions

For the most accurate hardware monitoring, it is recommended to run Proxmox Monitor **directly on the Proxmox host** rather than inside an isolated container.

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/aa7u/proxmox-monitor.git
cd proxmox-monitor
```

## 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create the environment file:

```bash
nano .env
```

Add:

```env
DISCORD_TOKEN=your_discord_bot_token
ALERT_CHANNEL_ID=your_discord_channel_id
```

Replace the placeholder values with your actual Discord credentials.

### 🔐 Security Warning

**Never commit `.env` or your Discord Bot Token to GitHub.**

Make sure `.env` is included in `.gitignore`.

---

## 5. Start the Monitor

```bash
python3 monitor.py
```

When successfully connected, the bot will send:

```text
🟢 MONITOR ONLINE

Proxmox monitoring is now active.
```

---

# ⚙️ Configuration

Monitoring thresholds and scheduling options can be configured directly in `monitor.py`.

### Default Configuration

```python
CPU_LIMIT = 95
RAM_LIMIT = 95
DISK_LIMIT = 95
TEMP_LIMIT = 95
BATTERY_LIMIT = 20

CHECK_INTERVAL = 10

REPORT_HOUR = 21
REPORT_MINUTE = 0

REPORT_MAX_DAYS = 30

SPEEDTEST_INTERVAL = 15 * 60
```

### Configuration Reference

| Setting              | Default | Description                 |
| -------------------- | ------: | --------------------------- |
| `CPU_LIMIT`          |   `95%` | CPU alert threshold         |
| `RAM_LIMIT`          |   `95%` | RAM alert threshold         |
| `DISK_LIMIT`         |   `95%` | Disk alert threshold        |
| `TEMP_LIMIT`         |  `95°C` | Temperature alert threshold |
| `BATTERY_LIMIT`      |   `20%` | Low battery threshold       |
| `CHECK_INTERVAL`     |   `10s` | Monitoring frequency        |
| `SPEEDTEST_INTERVAL` |   `15m` | Speed-test frequency        |
| `REPORT_MAX_DAYS`    |    `30` | Maximum report retention    |

---

# 🔐 Discord Bot Configuration

Create a Discord application and configure a bot through the Discord Developer Portal.

Invite the bot to your server with the required permissions.

The bot requires permission to:

* View the target channel
* Send messages
* Embed links
* Use application commands

After adding the bot to your server, configure:

```env
DISCORD_TOKEN=your_bot_token
ALERT_CHANNEL_ID=your_channel_id
```

---

# ⚙️ Running as a systemd Service

For production servers and homelab deployments, running Proxmox Monitor as a **systemd service** is recommended.

Create the service:

```bash
sudo nano /etc/systemd/system/proxmox-monitor.service
```

Example configuration:

```ini
[Unit]
Description=Proxmox Monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/proxmox-monitor
EnvironmentFile=/opt/proxmox-monitor/.env
ExecStart=/opt/proxmox-monitor/.venv/bin/python /opt/proxmox-monitor/monitor.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable the service:

```bash
sudo systemctl enable proxmox-monitor
```

Start the monitor:

```bash
sudo systemctl start proxmox-monitor
```

Check the service:

```bash
sudo systemctl status proxmox-monitor
```

Follow the logs:

```bash
journalctl -u proxmox-monitor -f
```

---

# 🔍 Monitoring Workflow

The monitoring engine continuously evaluates the current system state.

```text
Every 10 seconds
       │
       ▼
Collect system metrics
       │
       ├── CPU
       ├── RAM
       ├── Disk
       ├── Temperature
       ├── Battery
       ├── AC Power
       └── Internet
       │
       ▼
Evaluate thresholds
and state changes
       │
       ├── Normal
       │     └── Continue monitoring
       │
       └── Problem detected
             │
             ▼
        Discord Alert
```

Critical resource alerts use cooldown logic to prevent Discord spam while a condition remains active.

---

# 📁 Project Structure

```text
proxmox-monitor/
│
├── monitor.py
├── requirements.txt
├── env.example
├── .gitignore
└── monitor_state.json
```

### `monitor.py`

Main application containing:

* System monitoring
* Discord bot
* Alert handling
* Internet monitoring
* Speed testing
* Daily reports
* `/status` command
* Monitoring loops

### `env.example`

Example environment configuration.

### `requirements.txt`

Python package dependencies.

### `monitor_state.json`

Stores reporting state so the daily reporting cycle can continue across application restarts.

---

# ⚠️ Hardware & Platform Notes

## 🌡️ Temperature

Temperature availability depends on:

* Linux kernel support
* Hardware sensors
* `psutil`
* Available sensor interfaces

If no compatible temperature sensor is exposed, the monitor may report:

```text
N/A
```

## 🔋 Battery

Battery monitoring is primarily useful on physical systems that expose battery information.

The monitor also checks the Linux AC power state and can fall back to `psutil` where appropriate.

## 🌐 Internet Monitoring

If the server loses Internet connectivity completely, Discord alerts cannot be transmitted during the outage.

When connectivity is restored, the monitor detects the recovery and sends a notification.

---

# 🔒 Security Considerations

Protect your Discord credentials at all times.

Use environment variables:

```env
DISCORD_TOKEN=...
ALERT_CHANNEL_ID=...
```

Do **not** hard-code secrets inside `monitor.py`.

Before deploying on a production Proxmox host, review:

* File permissions
* systemd service permissions
* Network access
* Discord bot permissions
* Environment-file permissions
* Host security configuration

---

# 🗺️ Roadmap

Planned or potential improvements include:

* [ ] Proxmox API integration
* [ ] VM monitoring
* [ ] LXC monitoring
* [ ] ZFS health monitoring
* [ ] SMART disk health checks
* [ ] Network interface monitoring
* [ ] Historical metrics
* [ ] Web dashboard
* [ ] Configurable thresholds through `.env`
* [ ] Multiple Discord channels
* [ ] Alert severity levels
* [ ] Docker deployment
* [ ] Prometheus integration
* [ ] Grafana dashboards
* [ ] Multi-node Proxmox monitoring
* [ ] Automatic recovery notifications

---

# 🤝 Contributing

Contributions, bug reports, feature requests, and improvements are welcome.

### Fork the repository

Create your feature branch:

```bash
git checkout -b feature/my-feature
```

Commit your changes:

```bash
git commit -m "Add my feature"
```

Push the branch:

```bash
git push origin feature/my-feature
```

Then open a Pull Request.

---

# 🐛 Reporting Issues

If you discover a bug or have a feature request, please open an issue in the repository.

Include relevant information such as:

* Linux distribution
* Python version
* Proxmox version
* Error messages or logs
* Steps to reproduce the issue

**Never include your Discord Bot Token, credentials, or other secrets in an issue.**

---

# 📄 License

This project is provided as open-source software.

See the repository for the applicable license information.

---

# ⭐ Support the Project

If Proxmox Monitor is useful for your infrastructure:

* ⭐ Star the repository
* 🐛 Report bugs
* 💡 Suggest features
* 🔧 Submit Pull Requests
* 📢 Share the project with other Proxmox and homelab users

---

# 👨‍💻 Author

**aa7u**

Built for lightweight **Proxmox, Linux, and homelab infrastructure monitoring**.

---

<div align="center">

### 🖥️ Proxmox Monitor

**Monitor your infrastructure. Detect problems early. Stay informed.**

</div>
