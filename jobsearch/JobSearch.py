import requests
from pathlib import Path
import pandas as pd
import datetime as dt
from tqdm import tqdm
import re
import time
from collections import Counter
import sqlite3
from database import Database

def get_data_dir() -> Path:
    """
    Returns the path to the user's .jobsearch/Job_Listings directory.
    Creates it if it does not already exist.
    """
    home = Path.home()
    data_dir = home / ".jobsearch" / "Job_Listings"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

class JobSearch:
    """
    Searches for job listings using SerpApi's Google Jobs API.

    Attributes:
        api_key (str): SerpApi API Key.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initializes the client with the url and validates the API Key.

        Args:
            api_key (str): Your SerpApi API Key

        Raises:
            ValueError: If the API key is invalid.
        """

        self.url = "https://serpapi.com/search.json"
        self.api_key = api_key

        if not self.validate_key(api_key):
            raise ValueError("Invalid key")

    @staticmethod
    def validate_key(api_key: str) -> bool:
        """
        Validates your API key by using a test request.

        Args:
            api_key (str): SerpApi API Key to validate

        Returns:
            bool: True if key is valid, False if not.
        """

        url = "https://serpapi.com/search.json"
        params = {
            "engine": "google_jobs",
            "q": "test",
            "hl": "en",
            "api_key": api_key,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if "error" in data:
                print(f"API key error: {data['error']}")
                return False
            return True
        
        except requests.RequestException as e:
            print(f"WARNING: API KEY check failed. Error: {e}")
            return False

    def _get_page_with_retry(self, params: dict, max_retries: int = 5):
        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(self.url, params=params)
                data = response.json()

                if "error" in data and "not ready" in data["error"].lower():
                    wait = data.get("retry_after", 2)
                    print(
                        f"Pagination not ready. Retrying in {wait}s... (Attempt {attempt})"
                    )
                    time.sleep(wait)
                    continue

                if data.get("status") == "Processing":
                    wait = data.get("retry_after", 2)
                    print(
                        f"Page still processing. Waiting {wait}s... (Attempt {attempt})"
                    )
                    time.sleep(wait)
                    continue

                return data

            except requests.RequestException as e:
                print(f"Request error on attempt {attempt}: {e}")
                time.sleep(1)

        print("Max retries reached. Returning last response (may be incomplete).")
        return data if "data" in locals() else {}

    def search(self, job_title: str, location: str, save: bool = False) -> pd.DataFrame:
        """
        Searches for job listings within any specified state in the United States.

        Args:
            job_title (str): Career/Job title you want to search.
            location (str): The state you want your job search to take place.
            save (bool): Whether you want to save results to your computer.

        Returns:
            pd.DataFrame: DataFrame of all search results.
        """
        job_list = []
        next_page_token = None
        q = f"{job_title} {location}"

        safe_title = job_title.replace(" ", "_")
        safe_location = location.replace(" ", "_")

        with tqdm(desc="Fetching pages", unit="pages") as pbar:
            while True:
                params = {
                    "engine": "google_jobs",
                    "q": q,
                    "hl": "en",
                    "api_key": self.api_key,
                }

                if next_page_token:
                    params["next_page_token"] = next_page_token

                results = self._get_page_with_retry(params)

                jobs = results.get("jobs_results", [])
                if not jobs:
                    break

                for job in jobs:
                    job_list.append(
                        {
                            "job_title": job.get("title"),
                            "company": job.get("company_name"),
                            "location": job.get("location"),
                            "qualifications": job.get("job_highlights", [{}])[0].get(
                                "items", []
                            ),
                            "salary": job.get("detected_extensions", {}).get("salary"),
                            "description": job.get("description"),
                            "link": job.get("share_link"),
                        }
                    )

                next_page_token = results.get("serpapi_pagination", {}).get(
                    "next_page_token"
                )

                pbar.update(1)

                if not next_page_token:
                    break

            job_df = pd.DataFrame(job_list)

            if save:
                today = dt.datetime.today().strftime("%Y-%m-%d")
                filename = f"{safe_location}_{safe_title}_jobs_{today}.csv"

                save_dir = get_data_dir()
                save_path = save_dir / filename
                job_df.to_csv(save_path, index=False)

                print(f"\nSaved CSV to: {save_path}\n")

            return job_df

    def search_all_states(self, job_title: str, save: bool = False) -> pd.DataFrame:
        states = [
            "Alabama",
            "Alaska",
            "Arizona",
            "Arkansas",
            "California",
            "Colorado",
            "Connecticut",
            "Delaware",
            "Florida",
            "Georgia",
            "Hawaii",
            "Idaho",
            "Illinois",
            "Indiana",
            "Iowa",
            "Kansas",
            "Kentucky",
            "Louisiana",
            "Maine",
            "Maryland",
            "Massachusetts",
            "Michigan",
            "Minnesota",
            "Mississippi",
            "Missouri",
            "Montana",
            "Nebraska",
            "Nevada",
            "New Hampshire",
            "New Jersey",
            "New Mexico",
            "New York",
            "North Carolina",
            "North Dakota",
            "Ohio",
            "Oklahoma",
            "Oregon",
            "Pennsylvania",
            "Rhode Island",
            "South Carolina",
            "South Dakota",
            "Tennessee",
            "Texas",
            "Utah",
            "Vermont",
            "Virginia",
            "Washington",
            "West Virginia",
            "Wisconsin",
            "Wyoming",
        ]

        today = dt.datetime.today().strftime("%Y-%m-%d")
        safe_title = job_title.replace(" ", "_")
        save_dir = get_data_dir()

        all_jobs = []

        for state in tqdm(states, desc="Searching through states...", unit="state"):
            state_df = self.search(job_title, state, save=False)

            if not state_df.empty:
                state_df["state"] = state
                all_jobs.append(state_df)

                if save:
                    state_safe = state.replace(" ", "_")
                    state_file_path = save_dir / f"{state_safe}_{safe_title}_jobs_{today}.csv"
                    state_df.to_csv(state_file_path, index=False)
                    print(f"Saved {state} CSV to: {state_file_path}")

        combined_jobs = (
            pd.concat(all_jobs, ignore_index=True) if all_jobs else pd.DataFrame()
        )

        if save:
            filename = f"ALL_STATES_{safe_title}_jobs_{today}.csv"
            save_path = save_dir / filename
            combined_jobs.to_csv(save_path, index=False)

            print(f"Saved combined CSV to: {save_path}\n")

        return combined_jobs


class Clean:
    def __init__(self) -> None:
        self.data_folder = get_data_dir()

    def create_dataset(
        self,
        job_title: str,
        state: str | None = None,
        all_states: bool = False,
        save: bool = False,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
        date: dt.datetime | None = None,
    ) -> pd.DataFrame:
        """
        Loads and compiles job listing CSV files into a single pandas DataFrame.

        This method searches the 'Job_Listings' directory for CSV files that match
        the specified job titles, state, and optional date filters, then merges
        them into one unified dataset.

        Args:
            job_title (str): The job title to filter by (ex., "Cybersecurity").
            state (str, optional): the state to filter by. (Must omit if
                all_states=True).
            all_states (bool): If True, loads data from all states instead of
                specific state.
            save (bool): Whether you want to save the dataset as CSV
            year (int, optional): Filter by year (YYYY).
            month (int, optional): Filter by month (MM). Requires year.
            day (int, optional): Filter by day (DD). Requires year & month.
            date (datetime, optional): Full date object instead of
                year/month/day arguments.

        Returns:
            pandas.DataFrame: The  DataFrame containing the merged job listing data.

        Raises:
            ValueError: If both state and all_states are specified, or neither is.
        """

        # Validate whether all_states or specified state. Can't have both.
        valid = (all_states and state is None) or (not all_states and state is not None)
        if not valid:
            raise ValueError(
                "You must specify either 'state' OR  all_states=True, but not both"
            )

        # Converts job title into a string suited for the CSV file creation.
        job_title_safe = job_title.replace(" ", "_")

        # Determine dataset label
        if all_states:
            dataset_label = "*"
        else:
            dataset_label = state.replace(" ", "_")

        prefix = f"{dataset_label}_{job_title_safe}_jobs_"

        # If a full date was passed, break it apart.
        if date:  
            year = date.year
            month = date.month
            day = date.day

        # Validate date filtering
        if (month or day) and not year:
            raise ValueError("Year is required when filtering by month or day.")

        # Create the file patten for the CSV file.
        if year and month and day:
            file_pattern = f"{prefix}{year}-{month:02d}-{day:02d}.csv"
        elif year and month:
            file_pattern = f"{prefix}{year}-{month:02d}-*.csv"
        elif year:
            file_pattern = f"{prefix}{year}-*.csv"
        else:
            file_pattern = f"{prefix}*.csv"


        # List containing the specified files.
        files = list(self.data_folder.glob(file_pattern))
        if not files:
            print("No data files found.")
            return pd.DataFrame()

        datasets = []

        # Loop to read through all CSV files and convert into a pandas DataFrame.
        for f in tqdm(files, desc="Loading job data", unit="file"):
            try:
                df = pd.read_csv(f)
                datasets.append(df)
            except pd.errors.EmptyDataError:
                print(f"\nEmpty CSV skipped: {f}")
                continue

        # Combine the DataFrames into one.
        combined_df = (
            pd.concat(datasets, ignore_index=True) if datasets else pd.DataFrame()
        )

        # Salary parsing column expansion
        if not combined_df.empty and "salary" in combined_df.columns:
            parsed = combined_df["salary"].apply(self.parse_salary)
            parsed_df = parsed.apply(pd.Series)
            combined_df = pd.concat([combined_df, parsed_df], axis=1)

        if save:
            today = dt.datetime.today().strftime("%Y-%m-%d")
            filename  = f"{dataset_label}_{job_title_safe}_dataset_{today}.csv"
            save_path = self.data_folder / filename

            combined_df.to_csv(save_path, index=False)
            print(f"\nSaved compiled dataset to: {save_path}\n")

        print(f"\nCombined dataset created with {len(combined_df)} rows.\n")

        return combined_df

    def parse_salary(self, s: str) -> dict:
        """
        Parse raw salary text into numeric values

        Handles formats such as:
            "130K-160K a year"
            "30.00-37.50 an hour"
            "6,211-15,211 a month"
            "90K a year"
            "US$132K-US$180K a year"
            "$65K-$90K a year"

        Args:
            s (str): Raw salary string from the dataset.

        Returns:
            dict: A dictionary containing:
                - min_raw (float or None): Minimum salary value.
                - max_raw (float or None): Maximum salary value.
                - avg_value (float or None): Average of min and max.
                - annualized_avg (float or None): Annualized salary.
                - period (str or None): "hour", "month", "year"
        """

        # If salary is missing OR not a string, return None.
        if not isinstance(s, str) or s.strip() == "":
            return {
                k: None
                for k in [
                    "min_raw",
                    "max_raw",
                    "avg_value",
                    "min_annualized",
                    "max_annualized",
                    "annualized_avg",
                    "period",
                ]
            }

        original = s  # Stores the original for period detection.
        s = re.sub(r"\(.*?\)", "", s)

        # Removes extra characters in order to convert sting characters into a float.
        s = s.replace(",", "").replace("US$", "").replace("$", "").strip()

        # Determines the pay period from the original string.
        # Uses regex to check for "hour" or "hr" safely.

        text = original.lower()

        if re.search(r"hour|/hr|/h|\bhr\b", text):
            period = "hour"
        elif re.search(r"\bday\b|/day|daily\b", text):
            period = "day"
        elif re.search(r"\bweek\b|/week|/wk\b", text):
            period = "week"
        elif "month" in text:
            period = "month"
        elif re.search(r"\byr\b|/yr|per year|a year|\bannually\b|\bannual\b", text):
            period = "year"
        else:
            period = "year"

        # --------------------------
        # REGEX EXPLANATION
        #
        # \d: Matches any digit (0-9)
        # .: Matches any character
        # []: Character set (matches any single character within the brackets)
        # +: Matches 1 or more occurences of the preceding element
        # (): Grouping (Captures the matched content)
        # ?: Matches 0 or 1 occurrence of the preceding elemtent
        # \s: Matches any whitespace character
        # *: Matches 0 or more occurences of the preceding element
        #
        # --------------------------
        #
        # ([\d\.]+k?)   → Capture a number that may include decimals and optional 'k'
        # \s*           → Allow optional spaces
        # [–-]          → Match either a hyphen (-) or an EN dash (–)
        # \s*           → Optional spaces
        # ([\d\.]+k?)   → Capture the second number in the salary range
        #
        # This detects pairs like:
        #     "130k–160k"
        #     "30.00-37.50"
        #     "6211–15211"
        # --------------------------

        range_match = re.findall(
            r"([\d\.]+k?)\s*[–-]\s*([\d\.]+k?)", s, flags=re.IGNORECASE
        )

        # Salary appears as a range (130K-160K)
        if range_match:
            low, high = range_match[0]

            low = self.convert_number(low)
            high = self.convert_number(high)

        # Salary appears as a single number ('90K a year' or '45/hr')
        else:
            single_match = re.findall(r"([\d\.]+k?)", s, flags=re.IGNORECASE)
            if not single_match:
                return {
                    k: None
                    for k in [
                        "min_raw",
                        "max_raw",
                        "avg_value",
                        "min_annualized",
                        "max_annualized",
                        "annualized_avg",
                        "period",
                    ]
                }

            low = high = self.convert_number(single_match[0])

        # Compute averages
        avg = (low + high) / 2

        # Convert to annual salary based on the pay period
        if period == "hour":
            min_annualized = low * 40 * 52
            max_annualized = high * 40 * 52
            annualized_avg = avg * 40 * 52  # 40 hours * 52 weeks
        elif period == "day":
            min_annualized = low * 260
            max_annualized = high * 260
            annualized_avg = avg * 260
        elif period == "week":
            min_annualized = low * 52
            max_annualized = high * 52
            annualized_avg = avg * 52
        elif period == "month":
            min_annualized = low * 12
            max_annualized = high * 12
            annualized_avg = avg * 12
        else:
            min_annualized = low
            max_annualized = high
            annualized_avg = avg

        return {
            "min_raw": low,
            "max_raw": high,
            "avg_value": round(avg, 2),
            "min_annualized": round(min_annualized, 2),
            "max_annualized": round(max_annualized, 2),
            "annualized_avg": round(annualized_avg, 2),
            "period": period,
        }

    def convert_number(self, value: str) -> float:
        """
        Converts a numeric value from a dataset into a float.

        Handles:
            - K notation ("130K" -> 130000)
            - Decimal values ("37.50" -> 37.5)
            - Plain numbers (6211)

        Args:
            value (str): The numeric string.

        Returns:
            float: The numeric string converted to a float.
        """

        value = value.strip().lower()

        # Convert K-notation to a value
        if value.endswith("k"):
            return float(value[:-1]) * 1000

        # Convert simple number to a float
        return float(value)

    def filterdesc(self, df: pd.DataFrame, *keywords: str) -> pd.DataFrame:
        """
        This method loads a compiled dataset for the specified job title (across all
        states), filters through job descriptions, and then computes how frequently
        each keyword appears in the full dataset.

        Args:
            job_title (str): Job you wish to filter through
            *keywords (str): Any number of words you wish to search

        Returns:
            pandas.DataFrame:
                A DataFrame containing, for each keyword:
                    - keyword (str): The keyword searched.
                    - count (int): Total number of jobs containing the keyword.
                    - percent_total (float): Percentage of all job listing mentions.
                    - percent_filtered (float): Percentage of Filtered rows

                Example structure:
                    keyword | count | percent_total | percent_filtered
                    ----------------------------------------------------
                    python  | 382   | 81.20          | 92.40
                    splunk  | 120   | 25.52          | 45.00

            If no data or keywords provided, returns an empty DataFrame.

        Notes:
            - Search case-insensitive.
        """
        # If dataset is empty OR no keywords, return empty DataFrame
        if df.empty or not keywords:
            return pd.DataFrame()

        desc = df["description"].fillna("").astype(str).str.lower()

        # Allow for regex to treat keywords literally
        safe_keywords = [re.escape(k.lower()) for k in keywords]

        # Build regex pattern matching ANY of the keywords
        filter_keywords = r"(%s)" % "|".join(safe_keywords)
        result = desc.str.contains(filter_keywords, na=False)
        result_rows = result.sum()
        df_rows = len(df)

        # Count each keyword individually
        keyword_stats = []
        for kw in keywords:
            safe_kw = re.escape(kw.lower())

            occurrences = desc.str.count(safe_kw).sum()
            # Count how many jobs contain this keyword
            count = int(desc.str.contains(safe_kw, regex=True).sum())

            # Store results in a dictionary
            keyword_stats.append(
                {
                    "keyword": kw,
                    "occurrences": int(occurrences),
                    "count": count,
                    "percent_total": round((count / df_rows) * 100, 2)
                    if df_rows
                    else 0,
                    "percent_filtered": round((count / result_rows) * 100, 2)
                    if result_rows > 0
                    else 0,
                }
            )

        # Convert list into a DataFrame
        kw_df = pd.DataFrame(keyword_stats)
        kw_df = kw_df.sort_values(
            by=["occurrences", "count"], ascending=[False, False]
        ).reset_index(drop=True)

        return kw_df

    def salary_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame()

        min_salary = pd.to_numeric(df["min_annualized"], errors="coerce")
        max_salary = pd.to_numeric(df["max_annualized"], errors="coerce")
        avg_salary = pd.to_numeric(df["annualized_avg"], errors="coerce")

        stats = pd.DataFrame(
            {
                "min_salary_median": [min_salary.median()],
                "min_salary_mean": [min_salary.mean()],
                "max_salary_median": [max_salary.median()],
                "max_salary_mean": [max_salary.mean()],
                "avg_salary_median": [avg_salary.median()],
                "avg_salary_mean": [avg_salary.mean()],
                "count": [len(df)],
            }
        )

        salary_cols = [col for col in stats.columns if col != "count"]

        stats[salary_cols] = stats[salary_cols].applymap(
            lambda x: f"${x:,.2f}" if pd.notnull(x) else x
        )

        return stats
    
    def import_csv_folder_to_db(self):
        folder = self.data_folder
        csv_files = list(folder.glob("*.csv"))

        if not csv_files:
            print("No CSV files found in Job_Listings.")
            return
        
        db = Database()

        for csv in csv_files:
            filename = csv.name

            if db.file_already_imported(filename):
                print(f"Skipping {filename} (already imported).")
                continue

            print(f"Importing {filename}")

            df = pd.read_csv(csv)

            # Add parsed salary columns if they are missing
            if "salary" in df.columns:
                df["salary"] = df["salary"].fillna("").astype(str)
                parsed = df["salary"].apply(self.parse_salary)
                parsed_df = parsed.apply(pd.Series)
                df = pd.concat([df, parsed_df], axis=1)

            if "state" not in df.columns:
                df["state"] = None

            # Add date extracted from filename
            date_match = re.search(r"\d{4}-\d{2}-\d{2}", csv.stem)
            df["date_added"] = date_match.group(0) if date_match else None

            db.insert_dataframe(df)

            db.mark_file_imported(filename)

        db.close()
        print("\nAll CSV files imported into the database.\n")