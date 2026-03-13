from src.database import setup_database
from src.engine.scanner import scan_network


def main() -> None:
    print("Starting device scanner...")

    engine, sessionLocal = setup_database()
    scan_network()


if __name__ == "__main__":
    main()
