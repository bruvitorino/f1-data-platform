from src.marts.driver_performance import main as driver_performance_pipeline
from src.marts.team_performance import main as team_performance_pipeline


def run_mart_pipeline() -> None:
    """Build and validate all registered Data Marts."""

    print("=" * 80)
    print("Starting Data Marts Pipeline")
    print("=" * 80)

    print("\nBuilding Driver Performance Mart...")
    driver_performance_pipeline()
    print("Driver Performance Mart completed.")

    print("\nBuilding Team Performance Mart...")
    team_performance_pipeline()
    print("Team Performance Mart completed.")

    print("\n" + "=" * 80)
    print("Data Marts Pipeline completed successfully.")
    print("=" * 80)


def main() -> None:
    """Run the Data Marts pipeline."""

    run_mart_pipeline()


if __name__ == "__main__":
    main()