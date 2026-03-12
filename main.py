from scanner import scan_network
from database import database_manager


def main() -> None:
    print("Starting device scanner...")
    devices = scan_network()
    database_manager(devices)


if __name__ == "__main__":
    main()
