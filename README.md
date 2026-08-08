🖥️ Proxmox Monitor

Lightweight, real-time Proxmox server monitoring and Discord alert system built with Python.

Proxmox Monitor continuously watches your server’s health and sends important events directly to a Discord channel.

It is designed to be simple, lightweight, and easy to deploy on a Proxmox host or Linux server.

⸻

✨ Features

📊 System Monitoring

Continuously monitors:

* ⚙️ CPU utilization
* 🧠 RAM utilization
* 💾 Disk utilization
* 🌡️ System temperature
* 🔋 Battery level
* 🔌 Charger / AC power status
* 🌐 Internet connectivity

The default monitoring interval is 10 seconds.

🚨 Discord Alerts

Automatically sends Discord embeds when important events occur.

Alerts include:

* 🔴 High CPU usage
* 🔴 High RAM usage
* 🔴 High disk usage
* 🌡️ Critical temperature
* 🔋 Low battery
* 🔌 Charger connected
* 🔌 Charger disconnected
* 🌐 Internet restored
* 🟢 Monitor started successfully

Alerts include timestamps and a clean Discord Embed layout.

🌐 Internet Monitoring

The monitor checks Internet connectivity and detects when the connection goes offline or comes back online.

Connectivity is tested against a public DNS endpoint.

📡 Internet Speed Testing

Internet performance is automatically measured every 15 minutes.

The monitor records:

* ⬇️ Download speed
* ⬆️ Upload speed
* 📶 Ping
* 🌍 Speed-test server

Speed measurements are displayed in the daily report and /status command.

📅 Daily Server Reports

A daily Discord report provides a snapshot of the server’s current health.

The report includes:

Metric	Information
⚙️ CPU	Current CPU usage
🧠 RAM	Current memory usage
💾 Disk	Current disk usage
🌡️ Temperature	Current system temperature
🔋 Battery	Current battery percentage
🔌 Charger	AC / charger state
🌐 Internet	Online / Offline
⬇️ Download	Latest download speed
⬆️ Upload	Latest upload speed
📶 Ping	Latest latency

Reports are currently configured for a 30-day reporting period.

/status Command

Use the Discord slash command:

/status

to request the current server status.

Example:

🖥️ PROXMOX SERVER STATUS
⚙️ CPU           23.4%
🧠 RAM           41.2%
💾 Disk          58.7%
🌡️ Temperature   47.0°C
🔋 Battery       82%
🔌 Charger       🟢 Connected
🌐 Internet      🟢 Online
⬇️ Download      245.8 Mbps
⬆️ Upload        94.2 Mbps
📶 Ping           8 ms

⸻

🏗️ Architecture

┌───────────────────────────────┐
│        Proxmox / Linux        │
│                               │
│  ┌─────────────────────────┐  │
│  │     Proxmox Monitor     │  │
│  │         Python          │  │
│  └────────────┬────────────┘  │
│               │               │
│       ┌───────┴────────┐      │
│       │                │      │
│   System Stats      Network   │
│       │                │      │
│   CPU / RAM         Internet  │
│   Disk / Temp       Speedtest │
│   Battery / AC                 │
└───────────────┬───────────────┘
                │
                │ Discord API
                ▼
        ┌──────────────────┐
        │ Discord Channel  │
        │                  │
        │ 🚨 Alerts        │
        │ 📊 Daily Reports │
        │ 🖥️ /status       │
        └──────────────────┘

⸻

🛠️ Tech Stack

* Python
* psutil — system and hardware statistics
* discord.py — Discord bot and slash commands
* speedtest — Internet performance measurements
* python-dotenv — environment configuration
* asyncio — asynchronous monitoring loops

⸻

📋 Requirements

* Linux-based operating system
* Python 3.x
* Internet connectivity
* A Discord bot
* A Discord channel ID
* Permissions for the bot to send messages and use slash commands

For the most reliable hardware metrics, run the monitor directly on the Proxmox host rather than inside an isolated container.

⸻

🚀 Installation

1. Clone the repository

git clone https://github.com/aa7u/proxmox-monitor.git
cd proxmox-monitor

2. Create a virtual environment

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

Create a .env file:

nano .env

Add:

DISCORD_TOKEN=your_discord_bot_token
ALERT_CHANNEL_ID=your_discord_channel_id

Replace the values with your actual Discord Bot Token and target channel ID.

⚠️ Never commit .env or your Discord Bot Token to GitHub.

5. Start the monitor

python3 monitor.py

If everything is configured correctly, the bot will connect to Discord and send:

🟢 MONITOR ONLINE
Proxmox monitoring is now active.

⸻

⚙️ Configuration

The main monitoring thresholds can be adjusted directly in monitor.py.

Default values:

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

Thresholds

Setting	Default	Description
CPU_LIMIT	95%	CPU alert threshold
RAM_LIMIT	95%	RAM alert threshold
DISK_LIMIT	95%	Disk alert threshold
TEMP_LIMIT	95°C	Temperature alert threshold
BATTERY_LIMIT	20%	Low battery threshold
CHECK_INTERVAL	10s	Monitoring frequency
SPEEDTEST_INTERVAL	15m	Speed-test frequency
REPORT_MAX_DAYS	30	Maximum daily reports

⸻

🔐 Discord Bot Setup

Create a Discord application and bot, then invite it to your server with the required permissions.

The bot needs permission to:

* View the target channel
* Send messages
* Embed links
* Use application / slash commands

After the bot joins the server, copy:

1. Bot Token
2. Target Discord Channel ID

and place them in .env.

⸻

🧪 Running as a Service

For production or homelab usage, running the monitor through systemd is recommended.

Create:

sudo nano /etc/systemd/system/proxmox-monitor.service

Example:

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

Then:

sudo systemctl daemon-reload
sudo systemctl enable proxmox-monitor
sudo systemctl start proxmox-monitor

Check the service:

sudo systemctl status proxmox-monitor

View logs:

journalctl -u proxmox-monitor -f

⸻

🔍 Monitoring Logic

The monitor runs continuously and evaluates the current system state.

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
       ├── Charger
       └── Internet
       │
       ▼
Check thresholds / state changes
       │
       ├── Normal → Continue
       │
       └── Problem detected
                │
                ▼
          Discord Alert

A cooldown mechanism is used for critical resource alerts to avoid repeatedly spamming Discord while a condition remains active.

⸻

📁 Project Structure

proxmox-monitor/
├── monitor.py
├── requirements.txt
├── env.example
├── .gitignore
└── monitor_state.json

monitor.py

Main monitoring application containing:

* System monitoring
* Discord bot
* Alerts
* Speed testing
* Daily reports
* /status command
* Monitoring loops

env.example

Example environment configuration.

requirements.txt

Python package dependencies.

monitor_state.json

Stores daily-report state so the reporting cycle can continue across restarts.

⸻

⚠️ Important Notes

Temperature Support

Temperature availability depends on the Linux kernel, hardware sensors, and psutil support.

If no compatible sensor is exposed by the system, temperature may appear as:

N/A

Battery Monitoring

Battery information is mainly useful when the Proxmox host is running on hardware that exposes battery information.

The monitor also checks the Linux AC power state and falls back to psutil when necessary.

Internet Outage Detection

When the Internet connection is completely down, the monitor cannot send a Discord alert because Discord itself is unreachable.

Once connectivity returns, the monitor sends an:

🌐 INTERNET RESTORED

notification.

Speed Tests

Running frequent speed tests consumes network bandwidth and may generate additional traffic.

The default interval is 15 minutes.

⸻

🔒 Security

Never expose your Discord Bot Token.

Use environment variables:

DISCORD_TOKEN=...
ALERT_CHANNEL_ID=...

Do not hard-code secrets inside monitor.py.

Before deploying the monitor on a production Proxmox host, review the permissions, network access, and service configuration according to your environment.

⸻

🗺️ Roadmap

Potential future improvements:

* Proxmox API integration
* VM and LXC monitoring
* Storage / ZFS health monitoring
* SMART disk health checks
* Network interface monitoring
* Historical metrics
* Web dashboard
* Configurable alert thresholds via .env
* Multiple Discord channels
* Alert severity levels
* Docker deployment
* Prometheus / Grafana integration
* Multi-node Proxmox support
* Automatic recovery notifications

⸻

🤝 Contributing

Contributions, ideas, and improvements are welcome.

1. Fork the repository
2. Create a feature branch

git checkout -b feature/my-feature

3. Commit your changes

git commit -m "Add my feature"

4. Push the branch

git push origin feature/my-feature

5. Open a Pull Request

⸻

🐛 Issues

If you find a bug or have a feature request, please open an issue in the GitHub repository.

When reporting an issue, include:

* Linux distribution
* Python version
* Proxmox version
* Error message / logs
* Steps to reproduce the problem

Never include your Discord Bot Token or other secrets in an issue.

⸻

📄 License

This project is provided as open-source software.

See the repository for the applicable license information.

⸻

⭐ Support

If this project is useful to you:

* ⭐ Star the repository
* 🐛 Report bugs
* 💡 Suggest improvements
* 🔧 Submit pull requests
* 📢 Share it with other Proxmox / homelab users

⸻

👨‍💻 Author

aa7u

Built for lightweight Proxmox and homelab monitoring.

⸻

<p align="center">
  <strong>🖥️ Proxmox Monitor</strong><br>
  Monitor your infrastructure. Get alerted. Stay informed.
</p>
