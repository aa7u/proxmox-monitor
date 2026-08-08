import os
import time
import socket
import json
import asyncio
from datetime import datetime, timezone

import psutil
import discord
import speedtest

from discord.ext import commands, tasks
from dotenv import load_dotenv


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("ALERT_CHANNEL_ID", "0"))

CPU_LIMIT = 95
RAM_LIMIT = 95
DISK_LIMIT = 95
TEMP_LIMIT = 95
BATTERY_LIMIT = 20

CHECK_INTERVAL = 10

REPORT_HOUR = 21
REPORT_MINUTE = 0

REPORT_MAX_DAYS = 30

# قياس سرعة الإنترنت كل 15 دقيقة
SPEEDTEST_INTERVAL = 15 * 60

STATE_FILE = "monitor_state.json"


# =========================================================
# DISCORD
# =========================================================

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

alert_channel = None


# =========================================================
# STATE
# =========================================================

previous = {
    "internet": None,
    "charging": None,
    "battery_low": False,
}

last_alert = {}

speed_data = {
    "download": None,
    "upload": None,
    "ping": None,
    "server": None,
    "last_test": None,
}

last_speed_test = 0


# =========================================================
# REPORT STATE
# =========================================================

def load_report_state():

    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)

    except Exception:
        return {
            "started_at": datetime.now(timezone.utc).date().isoformat(),
            "reports_sent": 0,
            "last_report_date": None,
        }


report_state = load_report_state()


def save_report_state():

    try:
        with open(STATE_FILE, "w") as f:
            json.dump(report_state, f, indent=2)

    except Exception as e:
        print("Could not save report state:", e)


# =========================================================
# ALERT COOLDOWN
# =========================================================

def cooldown(key, seconds=60):

    now = time.time()

    if key in last_alert:

        if now - last_alert[key] < seconds:
            return False

    last_alert[key] = now

    return True


# =========================================================
# TEMPERATURE
# =========================================================

def get_temperature():

    try:

        temps = psutil.sensors_temperatures()

        values = []

        for entries in temps.values():

            for entry in entries:

                if entry.current is not None:
                    values.append(entry.current)

        if values:
            return max(values)

    except Exception:
        pass

    return None


# =========================================================
# BATTERY + CHARGER
# =========================================================

def get_battery():

    battery = None

    try:

        psutil_battery = psutil.sensors_battery()

        if psutil_battery:
            battery = psutil_battery.percent

    except Exception:
        pass

    charging = None

    # جهازك يستخدم ACAD
    try:

        with open(
            "/sys/class/power_supply/ACAD/online",
            "r"
        ) as f:

            charging = f.read().strip() == "1"

    except Exception:

        # fallback: psutil
        try:

            psutil_battery = psutil.sensors_battery()

            if psutil_battery:
                charging = psutil_battery.power_plugged

        except Exception:
            pass

    return battery, charging


# =========================================================
# INTERNET CONNECTION
# =========================================================

def internet_ok():

    try:

        socket.create_connection(
            ("1.1.1.1", 53),
            timeout=2
        )

        return True

    except Exception:

        return False


# =========================================================
# SPEED TEST
# =========================================================

def run_speedtest():

    global speed_data

    try:

        print("Running internet speed test...")

        st = speedtest.Speedtest()

        st.get_best_server()

        download = st.download()
        upload = st.upload()

        ping = st.results.ping

        server_name = st.results.server.get(
            "name",
            "Unknown"
        )

        speed_data = {
            "download": download / 1_000_000,
            "upload": upload / 1_000_000,
            "ping": ping,
            "server": server_name,
            "last_test": datetime.now(
                timezone.utc
            ).isoformat(),
        }

        print(
            f"Speed test: "
            f"Download={speed_data['download']:.1f} Mbps "
            f"Upload={speed_data['upload']:.1f} Mbps "
            f"Ping={speed_data['ping']:.0f} ms"
        )

    except Exception as e:

        print("Speed test failed:", e)


async def speedtest_loop():

    global last_speed_test

    while True:

        try:

            if internet_ok():

                await asyncio.to_thread(
                    run_speedtest
                )

                last_speed_test = time.time()

        except Exception as e:

            print("Speed test loop error:", e)

        await asyncio.sleep(SPEEDTEST_INTERVAL)


# =========================================================
# SYSTEM STATS
# =========================================================

def get_stats():

    cpu = psutil.cpu_percent(interval=None)

    ram = psutil.virtual_memory().percent

    disk = psutil.disk_usage("/").percent

    temperature = get_temperature()

    battery, charging = get_battery()

    return {
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "temperature": temperature,
        "battery": battery,
        "charging": charging,
    }


# =========================================================
# DISCORD ALERT
# =========================================================

async def send_alert(
    title,
    message,
    color=0xE74C3C
):

    if not alert_channel:
        return

    embed = discord.Embed(
        title=title,
        description=message,
        color=color,
        timestamp=datetime.now(timezone.utc)
    )

    embed.set_footer(
        text="Proxmox Monitor"
    )

    try:

        await alert_channel.send(
            embed=embed
        )

    except Exception as e:

        print(
            "Discord send error:",
            e
        )


# =========================================================
# MONITOR
# =========================================================

async def check_system():

    global previous

    stats = get_stats()

    print(
        f"CPU={stats['cpu']:.1f}% "
        f"RAM={stats['ram']:.1f}% "
        f"DISK={stats['disk']:.1f}% "
        f"TEMP={stats['temperature']} "
        f"BATTERY={stats['battery']} "
        f"CHARGING={stats['charging']}"
    )

    # -----------------------------------------------------
    # CPU
    # -----------------------------------------------------

    if stats["cpu"] >= CPU_LIMIT:

        if cooldown("cpu", 60):

            await send_alert(
                "🔴 CPU CRITICAL",
                f"CPU usage reached "
                f"**{stats['cpu']:.1f}%**"
            )

    # -----------------------------------------------------
    # RAM
    # -----------------------------------------------------

    if stats["ram"] >= RAM_LIMIT:

        if cooldown("ram", 60):

            await send_alert(
                "🔴 RAM CRITICAL",
                f"RAM usage reached "
                f"**{stats['ram']:.1f}%**"
            )

    # -----------------------------------------------------
    # DISK
    # -----------------------------------------------------

    if stats["disk"] >= DISK_LIMIT:

        if cooldown("disk", 60):

            await send_alert(
                "🔴 DISK CRITICAL",
                f"Disk usage reached "
                f"**{stats['disk']:.1f}%**"
            )

    # -----------------------------------------------------
    # TEMPERATURE
    # -----------------------------------------------------

    temperature = stats["temperature"]

    if temperature is not None:

        if temperature >= TEMP_LIMIT:

            if cooldown("temperature", 60):

                await send_alert(
                    "🌡️ TEMPERATURE CRITICAL",
                    f"Temperature reached "
                    f"**{temperature:.1f}°C**"
                )

    # -----------------------------------------------------
    # BATTERY
    # -----------------------------------------------------

    battery = stats["battery"]

    if battery is not None:

        if battery <= BATTERY_LIMIT:

            if not previous["battery_low"]:

                previous["battery_low"] = True

                await send_alert(
                    "🔋 BATTERY LOW",
                    f"Battery is at "
                    f"**{battery:.0f}%**"
                )

        elif battery > BATTERY_LIMIT:

            previous["battery_low"] = False

    # -----------------------------------------------------
    # CHARGER
    # -----------------------------------------------------

    charging = stats["charging"]

    if charging is not None:

        if previous["charging"] is not None:

            if charging != previous["charging"]:

                if charging:

                    await send_alert(
                        "🔌 CHARGER CONNECTED",
                        "The charger has been connected.",
                        0x2ECC71
                    )

                else:

                    await send_alert(
                        "🔌 CHARGER DISCONNECTED",
                        "The charger has been disconnected."
                    )

        previous["charging"] = charging

    # -----------------------------------------------------
    # INTERNET
    # -----------------------------------------------------

    online = internet_ok()

    if previous["internet"] is not None:

        if online and not previous["internet"]:

            await send_alert(
                "🌐 INTERNET RESTORED",
                "Internet connection is back online.",
                0x2ECC71
            )

        elif not online and previous["internet"]:

            # لا يمكن إرسال Discord أثناء انقطاع الإنترنت
            print(
                "Internet disconnected."
            )

    previous["internet"] = online


# =========================================================
# MONITOR LOOP
# =========================================================

@tasks.loop(seconds=CHECK_INTERVAL)
async def monitor_loop():

    try:

        await check_system()

    except Exception as e:

        print(
            "Monitoring error:",
            e
        )


@monitor_loop.before_loop
async def before_monitor():

    await bot.wait_until_ready()


# =========================================================
# DAILY REPORT
# =========================================================

async def send_daily_report():

    if not alert_channel:
        return

    if report_state["reports_sent"] >= REPORT_MAX_DAYS:
        return

    today = datetime.now(
        timezone.utc
    ).date().isoformat()

    if report_state["last_report_date"] == today:
        return

    stats = get_stats()

    temp = (
        f"{stats['temperature']:.1f}°C"
        if stats["temperature"] is not None
        else "N/A"
    )

    battery = (
        f"{stats['battery']:.0f}%"
        if stats["battery"] is not None
        else "N/A"
    )

    charger = (
        "🟢 Connected"
        if stats["charging"]
        else "🔴 Disconnected"
        if stats["charging"] is not None
        else "N/A"
    )

    internet = (
        "🟢 Online"
        if internet_ok()
        else "🔴 Offline"
    )

    download = (
        f"{speed_data['download']:.1f} Mbps"
        if speed_data["download"] is not None
        else "N/A"
    )

    upload = (
        f"{speed_data['upload']:.1f} Mbps"
        if speed_data["upload"] is not None
        else "N/A"
    )

    ping = (
        f"{speed_data['ping']:.0f} ms"
        if speed_data["ping"] is not None
        else "N/A"
    )

    report_number = (
        report_state["reports_sent"] + 1
    )

    embed = discord.Embed(
        title="📊 DAILY SERVER REPORT",
        description=(
            f"Daily report **{report_number}/"
            f"{REPORT_MAX_DAYS}**"
        ),
        color=0x3498DB,
        timestamp=datetime.now(timezone.utc)
    )

    embed.add_field(
        name="⚙️ CPU",
        value=f"`{stats['cpu']:.1f}%`",
        inline=True
    )

    embed.add_field(
        name="🧠 RAM",
        value=f"`{stats['ram']:.1f}%`",
        inline=True
    )

    embed.add_field(
        name="💾 Disk",
        value=f"`{stats['disk']:.1f}%`",
        inline=True
    )

    embed.add_field(
        name="🌡️ Temperature",
        value=f"`{temp}`",
        inline=True
    )

    embed.add_field(
        name="🔋 Battery",
        value=f"`{battery}`",
        inline=True
    )

    embed.add_field(
        name="🔌 Charger",
        value=charger,
        inline=True
    )

    embed.add_field(
        name="🌐 Internet",
        value=internet,
        inline=True
    )

    embed.add_field(
        name="⬇️ Download",
        value=f"`{download}`",
        inline=True
    )

    embed.add_field(
        name="⬆️ Upload",
        value=f"`{upload}`",
        inline=True
    )

    embed.add_field(
        name="📶 Ping",
        value=f"`{ping}`",
        inline=True
    )

    embed.set_footer(
        text="Proxmox Monitor • 30 Day Report"
    )

    try:

        await alert_channel.send(
            embed=embed
        )

        report_state["reports_sent"] += 1
        report_state["last_report_date"] = today

        save_report_state()

        print(
            f"Daily report sent "
            f"({report_number}/{REPORT_MAX_DAYS})"
        )

    except Exception as e:

        print(
            "Daily report error:",
            e
        )


async def daily_report_loop():

    while True:

        try:

            now = datetime.now()

            if (
                now.hour == REPORT_HOUR
                and now.minute == REPORT_MINUTE
            ):

                await send_daily_report()

        except Exception as e:

            print(
                "Daily report loop error:",
                e
            )

        await asyncio.sleep(30)


# =========================================================
# /STATUS
# =========================================================

@bot.tree.command(
    name="status",
    description="عرض حالة السيرفر وسرعة الإنترنت"
)
async def status(
    interaction: discord.Interaction
):

    stats = get_stats()

    temperature = (
        f"{stats['temperature']:.1f}°C"
        if stats["temperature"] is not None
        else "N/A"
    )

    battery = (
        f"{stats['battery']:.0f}%"
        if stats["battery"] is not None
        else "N/A"
    )

    charger = (
        "🟢 Connected"
        if stats["charging"]
        else "🔴 Disconnected"
        if stats["charging"] is not None
        else "N/A"
    )

    internet = (
        "🟢 Online"
        if internet_ok()
        else "🔴 Offline"
    )

    download = (
        f"{speed_data['download']:.1f} Mbps"
        if speed_data["download"] is not None
        else "Not tested yet"
    )

    upload = (
        f"{speed_data['upload']:.1f} Mbps"
        if speed_data["upload"] is not None
        else "Not tested yet"
    )

    ping = (
        f"{speed_data['ping']:.0f} ms"
        if speed_data["ping"] is not None
        else "N/A"
    )

    embed = discord.Embed(
        title="🖥️ PROXMOX SERVER STATUS",
        color=0x2ECC71
    )

    embed.add_field(
        name="⚙️ CPU",
        value=f"`{stats['cpu']:.1f}%`",
        inline=True
    )

    embed.add_field(
        name="🧠 RAM",
        value=f"`{stats['ram']:.1f}%`",
        inline=True
    )

    embed.add_field(
        name="💾 Disk",
        value=f"`{stats['disk']:.1f}%`",
        inline=True
    )

    embed.add_field(
        name="🌡️ Temperature",
        value=f"`{temperature}`",
        inline=True
    )

    embed.add_field(
        name="🔋 Battery",
        value=f"`{battery}`",
        inline=True
    )

    embed.add_field(
        name="🔌 Charger",
        value=charger,
        inline=True
    )

    embed.add_field(
        name="🌐 Internet",
        value=internet,
        inline=True
    )

    embed.add_field(
        name="⬇️ Download",
        value=f"`{download}`",
        inline=True
    )

    embed.add_field(
        name="⬆️ Upload",
        value=f"`{upload}`",
        inline=True
    )

    embed.add_field(
        name="📶 Ping",
        value=f"`{ping}`",
        inline=True
    )

    if speed_data["last_test"]:

        embed.add_field(
            name="🕒 Speed Test",
            value="Every 15 minutes",
            inline=False
        )

    embed.set_footer(
        text="Proxmox Monitor • 30 Day Edition"
    )

    await interaction.response.send_message(
        embed=embed
    )


# =========================================================
# READY
# =========================================================

@bot.event
async def on_ready():

    global alert_channel

    print(
        f"Connected as {bot.user}"
    )

    # Get Discord channel
    alert_channel = bot.get_channel(
        CHANNEL_ID
    )

    if alert_channel is None:

        try:

            alert_channel = await bot.fetch_channel(
                CHANNEL_ID
            )

        except Exception as e:

            print(
                "Could not find Discord channel:",
                e
            )

    # Sync slash commands
    try:

        await bot.tree.sync()

        print(
            "Slash commands synced."
        )

    except Exception as e:

        print(
            "Slash sync error:",
            e
        )

    # Start monitoring
    if not monitor_loop.is_running():

        monitor_loop.start()

    # Start speed test loop
    if not hasattr(
        bot,
        "speed_task"
    ) or bot.speed_task.done():

        bot.speed_task = asyncio.create_task(
            speedtest_loop()
        )

    # Start daily report
    if not hasattr(
        bot,
        "report_task"
    ) or bot.report_task.done():

        bot.report_task = asyncio.create_task(
            daily_report_loop()
        )

    await send_alert(
        "🟢 MONITOR ONLINE",
        "Proxmox monitoring is now active.",
        0x2ECC71
    )


# =========================================================
# START
# =========================================================

if not TOKEN:

    raise RuntimeError(
        "DISCORD_TOKEN is missing from .env"
    )


bot.run(TOKEN)
