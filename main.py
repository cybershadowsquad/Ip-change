import os
import re
import shutil
import socket
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

# -------------------------------
# 🔁 IPHopper - IP Changing Tool
# Created by Alok Thakur
# YouTube: Firewall Breaker
# -------------------------------

RED = "\033[31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
CYAN = "\033[1;36m"
RED_BOLD = "\033[1;31m"
RESET = "\033[0m"

PORTS = [9050, 9060, 9070, 9080, 9090]
CONTROL_PORTS = [9051, 9061, 9071, 9081, 9091]
PRIVOXY_PORT = 8118


def print_banner() -> None:
    print(f"{RED}██╗██████╗       ██╗  ██╗ ██████╗ ██████╗ ██████╗ ██████╗ ██████╗")
    print("██║██╔══██╗      ██║  ██║██╔═══██╗██╔══██╗██╔══██╗██╔══██╗██╔══██╗")
    print("██║██████╔╝█████╗███████║██║   ██║██████╔╝██████╔╝██████╔╝██████╔╝")
    print("██║██╔═══╝ ╚════╝██╔══██║██║   ██║██╔═══╝ ██╔═══╝ ██╔══██╗██╔══██╗")
    print("██║██║           ██║  ██║╚██████╔╝██║     ██║     ██║  ██║██║  ██║")
    print(f"╚═╝╚═╝           ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝{RESET}")
    print(f"{YELLOW}               🔁 IPHopper - IP Changing Tool 🔁{RESET}")
    print(f"{BLUE}         👨‍💻 Created by Alok Thakur | YouTube: Firewall Breaker{RESET}")
    print()


def kill_old_services() -> None:
    subprocess.run(["pkill", "tor"], check=False)
    subprocess.run(["pkill", "privoxy"], check=False)


def cleanup_and_prepare(home: Path) -> tuple[Path, Path]:
    tor_multi = home / ".tor_multi"
    privoxy_dir = home / ".privoxy"
    shutil.rmtree(tor_multi, ignore_errors=True)
    shutil.rmtree(privoxy_dir, ignore_errors=True)
    tor_multi.mkdir(parents=True, exist_ok=True)
    privoxy_dir.mkdir(parents=True, exist_ok=True)
    return tor_multi, privoxy_dir


def launch_tor_nodes(tor_multi: Path) -> None:
    print(f"{GREEN}[+] Launching Tor Nodes & Proxy Server...{RESET}")
    for i in range(len(PORTS)):
        tor_dir = tor_multi / f"tor{i}"
        tor_dir.mkdir(parents=True, exist_ok=True)
        torrc = tor_dir / "torrc"
        torrc.write_text(
            f"SocksPort {PORTS[i]}\n"
            f"ControlPort {CONTROL_PORTS[i]}\n"
            f"DataDirectory {tor_dir}\n"
            "CookieAuthentication 0\n",
            encoding="utf-8",
        )
        subprocess.Popen(
            ["tor", "-f", str(torrc)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(2)


def setup_privoxy(privoxy_dir: Path) -> None:
    config = privoxy_dir / "config"
    lines = [f"listen-address 127.0.0.1:{PRIVOXY_PORT}\n"]
    for port in PORTS:
        lines.append(f"forward-socks5 / 127.0.0.1:{port} .\n")
    config.write_text("".join(lines), encoding="utf-8")

    subprocess.Popen(
        ["privoxy", str(config)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def get_rotation_time() -> int:
    raw = input(f"{CYAN}Enter IP rotation interval (in seconds, min 5s): {RESET}").strip()
    if not re.fullmatch(r"[0-9]+", raw) or int(raw) < 5:
        print(f"{RED_BOLD}Invalid input! Using default 10 seconds.{RESET}")
        return 10
    return int(raw)


def request_new_identity(control_port: int) -> None:
    payload = b'AUTHENTICATE ""\r\nSIGNAL NEWNYM\r\nQUIT\r\n'
    try:
        with socket.create_connection(("127.0.0.1", control_port), timeout=5) as sock:
            sock.sendall(payload)
            sock.settimeout(2)
            try:
                sock.recv(1024)
            except socket.timeout:
                pass
    except OSError:
        pass


def fetch_current_ip() -> str:
    proxy = urllib.request.ProxyHandler(
        {
            "http": f"http://127.0.0.1:{PRIVOXY_PORT}",
            "https": f"http://127.0.0.1:{PRIVOXY_PORT}",
        }
    )
    opener = urllib.request.build_opener(proxy)
    try:
        with opener.open("https://api64.ipify.org", timeout=15) as response:
            return response.read().decode("utf-8", errors="replace").strip()
    except (urllib.error.URLError, OSError, ValueError):
        return ""


def rotate_forever(rotation_time: int) -> None:
    while True:
        for ctrl_port in CONTROL_PORTS:
            request_new_identity(ctrl_port)
        new_ip = fetch_current_ip()
        print(f"{GREEN}🌐 New IP: {new_ip} ✅{RESET}")
        print(f"{BLUE}[Proxy]: 127.0.0.1:{PRIVOXY_PORT} 🛰️{RESET}")
        time.sleep(rotation_time)


def main() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print_banner()

    kill_old_services()
    tor_multi, privoxy_dir = cleanup_and_prepare(Path.home())

    launch_tor_nodes(tor_multi)
    setup_privoxy(privoxy_dir)

    rotation_time = get_rotation_time()
    rotate_forever(rotation_time)


if __name__ == "__main__":
    main()