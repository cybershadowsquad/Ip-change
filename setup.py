import subprocess

YELLOW = "\033[1;33m"
GREEN = "\033[1;32m"
RESET = "\033[0m"


def run(command: list[str], check: bool = False) -> None:
    subprocess.run(command, check=check)


def main() -> None:
    print(f"{YELLOW}[+] Updating & Upgrading Termux Packages...{RESET}")
    # Mirrors `apt update -y && apt upgrade -y`: upgrade only runs if update succeeds
    run(["apt", "update", "-y"], check=True)
    run(["apt", "upgrade", "-y"], check=True)

    print(f"{YELLOW}[+] Installing tur-repo & Required Packages...{RESET}")
    run(["apt", "install", "tur-repo", "-y"])
    run(["apt", "install", "tor", "privoxy", "netcat-openbsd", "curl", "-y"])

    print(f"{GREEN}[✓] All dependencies installed successfully!{RESET}")


if __name__ == "__main__":
    main()