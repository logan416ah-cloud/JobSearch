from JobSearch import JobSearch, Clean
import argparse
from datetime import datetime


def main() -> None:
    parser = argparse.ArgumentParser(description="JobSearch CLI with subcommands")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # -----------------------------------------------------------------------
    search_parser = subparsers.add_parser("search", help="Search for jobs in a state")
    search_parser.add_argument(
        "--state",
        required=True,
        help="State to search (ex. 'New Jersey')",
    )
    search_parser.add_argument(
        "--job",
        required=True,
        help="Job title to search (ex. 'Cybersecurity Analyst')",
    )
    search_parser.add_argument(
        "--save",
        action="store_true",
        help="If set, save the results to a CSV",
    )

    # -----------------------------------------------------------------------
    create_dataset_parser = subparsers.add_parser(
        "create_dataset", help="Compile specified CSV files into one dataset"
    )

    # User must specify a --state OR --all
    state_group = create_dataset_parser.add_mutually_exclusive_group(required=True)
    state_group.add_argument("--state", help="State to compile (ex. 'New Jersey')")
    state_group.add_argument("--all", action="store_true", help="Use all US states")

    create_dataset_parser.add_argument(
        "--job",
        required=True,
        help="The job title to compile",
    )

    # Save flag
    create_dataset_parser.add_argument(
        "--save",
        action="store_true",
        help="If set, save the results to a CSV",
    )

    # Date filters
    create_dataset_parser.add_argument(
        "--year",
        type=int,
        help="Year (YYYY)",
    )
    create_dataset_parser.add_argument(
        "--month",
        type=int,
        help="Month (1-12)",
    )
    create_dataset_parser.add_argument(
        "--day",
        type=int,
        help="Day (1-31)",
    )
    create_dataset_parser.add_argument(
        "--date",
        type=str,
        help="Full date 'YYYY-MM-DD'",
    )

    args = parser.parse_args()

    if args.command == "search":
        api_key = input("Enter your API Key. ")
        js = JobSearch(api_key)
        df = js.search(args.job, args.state, save=args.save)
        print(df.head())

    elif args.command == "create_dataset":
        c = Clean()
        combined = c.create_dataset(
            args.job,
            state=args.state,
            all_states=args.all,
            save=args.save,
            year=args.year,
            month=args.month,
            day=args.day,
            date=args.date,
        )
        print(combined.head())


if __name__ == "__main__":
    main()
