# import psutil
# from datetime import datetime
# import sqlite3
# import os
# import time
# import subprocess
# import platform

# DB_NAME = "log.db"

# def init_db():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS system_log (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             timestamp TEXT,
#             cpu REAL,
#             memory REAL,
#             disk REAL,
#             ping_status TEXT,
#             ping_ms REAL
#         )
#     """)
#     conn.commit()
#     conn.close()

# def get_system_info():
#     now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     cpu = psutil.cpu_percent(interval=1)
#     memory = psutil.virtual_memory().percent
#     disk = psutil.disk_usage('/').percent
#     ping_status, ping_ms = ping_host("8.8.8.8")
#     return (now, cpu, memory, disk, ping_status, ping_ms)

# def ping_host(host):
#     try:
#         param = "-n" if platform.system().lower() == "windows" else "-c"
#         output = subprocess.check_output(["ping", param, "1", host], stderr=subprocess.DEVNULL).decode()
#         ms = parse_ping_time(output)
#         return ("UP", ms)
#     except:
#         return ("DOWN", -1)

# def parse_ping_time(output):
#     for line in output.splitlines():
#         if "time=" in line:
#             parts = line.split("time=")
#             if len(parts) > 1:
#                 try:
#                     return float(parts[1].split()[0])
#                 except ValueError:
#                     return -1
#     return -1
    
# def insert_log(data):
#     # TODO: Insert one row of system info into SQLite
#     pass

# def show_last_entries(limit=5):
#     # TODO: Retrieve and print the last few records from the database
#     pass

# if __name__ == "__main__":
#     init_db()
#     for _ in range(5):
#         row = get_system_info()
#         insert_log(row)
#         print("Logged:", row)
#         time.sleep(10)
#     show_last_entries()



import psutil
from datetime import datetime
import sqlite3
import os
import time
import subprocess
import platform

DB_NAME = "log.db"

def init_db():
    """Create the SQLite database and the system_log table (if they don't exist)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cpu REAL,
            memory REAL,
            disk REAL,
            ping_status TEXT,
            ping_ms REAL
        )
    """)
    conn.commit()
    conn.close()

def get_system_info():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent

    # Use a sensible root for disk usage on Windows vs. POSIX
    if platform.system().lower() == "windows":
        disk_path = "C:\\"
    else:
        disk_path = "/"
    disk = psutil.disk_usage(disk_path).percent

    ping_status, ping_ms = ping_host("8.8.8.8")
    return (now, cpu, memory, disk, ping_status, ping_ms)

def ping_host(host):
    try:
        system = platform.system().lower()
        if system == "windows":
            cmd = ["ping", "-n", "1", host]
        else:
            cmd = ["ping", "-c", "1", host]

        # universal_newlines=True returns a str instead of bytes
        output = subprocess.check_output(
            cmd, stderr=subprocess.DEVNULL, universal_newlines=True
        )
        ms = parse_ping_time(output)
        return ("UP", ms)
    except Exception:
        return ("DOWN", -1)

def parse_ping_time(output):
    for line in output.splitlines():
        if "time=" in line:
            parts = line.split("time=")
            if len(parts) > 1:
                try:
                    return float(parts[1].split()[0])
                except ValueError:
                    return -1
    return -1

def insert_log(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO system_log (timestamp, cpu, memory, disk, ping_status, ping_ms)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        data,
    )
    conn.commit()
    conn.close()

def show_last_entries(limit=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM system_log ORDER BY id DESC LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()

    print(f"... Last {limit} entries:")
    for row in reversed(rows):
        print(row)

if __name__ == "__main__":
    # Ensure the DB & table exist
    init_db()

    # Collect 5 samples, 10 seconds apart
    for _ in range(5):
        row = get_system_info()
        insert_log(row)
        print("Logged:", row)
        time.sleep(10)

    # Show the most recent 5 records
    show_last_entries()