from JobSearch import JobSearch, Clean
import argparse
from datetime import datetime


def main() -> None:
    parser = argparse.ArgumentParser(description="JobSearch CLI with subcommands")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # For search()
    search_parser = subparsers.add_parser(
        "search", help="Search for jobs in a single U.S. state"
    )

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

    search_parser.epilog = """
    Examples:
      python cli.py search --state "New York" --job "Cybersecurity Analyst"
      python cli.py search --state Texas --job Nurse --save
    """

    # For search_all_states()
    all_parser = subparsers.add_parser(
        "search_all", help="Search for jobs in ALL states"
    )

    all_parser.add_argument(
        "--job",
        required=True,
        help="Job title to search (ex. 'Cybersecurity Analyst')",
    )
    all_parser.add_argument(
        "--save",
        action="store_true",
        help="If set, save the results to a CSV",
    )

    all_parser.epilog = """
    Examples:
      python cli.py search_all --job "Cybersecurity Analyst"
      python cli.py search_all --job Nurse --save
    """

    # For create_dataset()
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
    create_dataset_parser.add_argument(
        "--save",
        action="store_true",
        help="If set, save the results to a CSV",
    )
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

    create_dataset_parser.epilog = """
    Examples:
      python cli.py create_dataset --state "New York" --job "Cybersecurity Analyst" --save
      python cli.py create_dataset --all --job Nurse --year 2025 --month 4 --save
    """

    # For filterdesc()
    filter_parser = subparsers.add_parser(
        "filter", help="Filter through job description for keywords"
    )

    state_group = filter_parser.add_mutually_exclusive_group(required=True)
    state_group.add_argument("--state", help="State to compile (ex. 'New Jersey')")
    state_group.add_argument("--all", action="store_true", help="Use all US states")

    filter_parser.add_argument(
        "--keywords",
        nargs="+",
        required=True,
        help="Any number of words you wish to search for",
    )
    filter_parser.add_argument(
        "--job",
        required=True,
        help="The job title to filter by",
    )
    filter_parser.add_argument(
        "--year",
        type=int,
        help="The year (YYYY) to filter by",
    )
    filter_parser.add_argument(
        "--month",
        type=int,
        help="The month (MM) to filter by",
    )
    filter_parser.add_argument(
        "--day",
        type=int,
        help="The day (DD) to filter by",
    )

    filter_parser.epilog = """
    Examples:
      python cli.py filter --keywords "python" "aws" "COMPTIA" --state "New York" --job "Cybersecurity Analyst"
      python cli.py filter --keywords "BSN" "trauma" "pediatrics" --all --job Nurse --year 2025 --month 4 
    """

    # For salary_stats()
    salary_stats_parser = subparsers.add_parser(
        "sstats", help="Show annualized salary stats (mean/median)"
    )

    state_group = salary_stats_parser.add_mutually_exclusive_group(required=True)
    state_group.add_argument("--state", help="State to compile (ex. 'New Jersey')")
    state_group.add_argument("--all", action="store_true", help="Use all US states")

    salary_stats_parser.add_argument(
        "--job",
        required=True,
        help="The job title to filter by",
    )

    salary_stats_parser.add_argument(
        "--year",
        type=int,
        help="The year (YYYY) to filter by",
    )
    salary_stats_parser.add_argument(
        "--month",
        type=int,
        help="The month (MM) to filter by",
    )
    salary_stats_parser.add_argument(
        "--day",
        type=int,
        help="The day (DD) to filter by",
    )

    salary_stats_parser.epilog = """
    Examples:
      python cli.py sstats --state "New York" --job "Cybersecurity Analyst"
      python cli.py sstats --all --job Nurse --year 2025 --month 4 
    """

    args = parser.parse_args()

    if args.command == "search":
        api_key = input("Enter your API Key. ")
        js = JobSearch(api_key)
        df = js.search(args.job, args.state, save=args.save)

        print(df.head())

    elif args.command == "search_all":
        api_key = input("Enter your API Key. ")
        js = JobSearch(api_key)
        df = js.search_all_states(args.job, save=args.save)

        print(df.head())

    elif args.command == "create_dataset":
        parsed_date = None

        if args.date:
            try:
                parsed_date = datetime.strptime(args.date, "%Y-%m-%d")
            except ValueError:
                print("ERROR. Date must be YYYY-MM-DD")
                return

        c = Clean()
        combined = c.create_dataset(
            args.job,
            state=args.state,
            all_states=args.all,
            save=args.save,
            year=args.year,
            month=args.month,
            day=args.day,
            date=parsed_date,
        )
        print(combined.head())

    elif args.command == "filter":
        c = Clean()

        combined = c.create_dataset(
            job_title=args.job,
            state=args.state,
            all_states=args.all,
            save=False,
            year=args.year,
            month=args.month,
            day=args.day,
            date=None,
        )

        print(c.filterdesc(combined, *args.keywords))
        print(f"\nKeywords searched across {len(combined)} job listings.\n")

    elif args.command == "sstats":
        c = Clean()

        combined = c.create_dataset(
            job_title=args.job,
            state=args.state,
            all_states=args.all,
            save=False,
            year=args.year,
            month=args.month,
            day=args.day,
            date=None,
        )

        print(c.salary_stats(combined))


if __name__ == "__main__":
    main()
