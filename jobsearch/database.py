import sqlite3
from pathlib import Path
import pandas as pd


DB_DIR = Path.home() / ".jobsearch"
DB_PATH = DB_DIR / "jobs.db"

class Database:
    def __init__(self):
        DB_DIR.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()
        self.init_db()

    def init_db(self):
        """Create table if it doesn't exist"""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_title TEXT,
                company TEXT,
                location TEXT,
                state TEXT,
                qualifications TEXT,
                description TEXT,
                salary TEXT,
                min_raw REAL,
                max_raw REAL,
                avg_value REAL,
                min_annualized REAL,
                max_annualized REAL,
                annualized_avg REAL,
                period TEXT,
                link TEXT UNIQUE,
                date_added TEXT
            )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS files_imported (
            filename TEXT PRIMARY KEY,
            imported_at TEXT             
            )
         """)
        
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_title ON jobs(job_title)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_state ON jobs(state)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_company ON jobs(company)")
        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_link ON jobs(link)")

        self.conn.commit()

    def insert_dataframe(self, df):
        """Insert a pandas DataFrame into the jobs table"""
        records = df.to_dict(orient="records")

        query = """
            INSERT OR IGNORE INTO jobs (
                job_title, company, location, state, description,
                salary, min_raw, max_raw, avg_value,
                min_annualized, max_annualized, annualized_avg,
                period, link, date_added
            ) VALUES (
                :job_title, :company, :location, :state, :description,
                :salary, :min_raw, :max_raw, :avg_value,
                :min_annualized, :max_annualized, :annualized_avg,
                :period, :link, :date_added
            )
        """

        self.cur.executemany(query, records)
        self.conn.commit()

    def query(self, sql, params=()):
        """General purpose SQL query method."""
        self.cur.execute(sql, params)
        return self.cur.fetchall()
    
    def get_jobs_by_title(self, title):
        """Retrieve all jobs matching a job title"""
        return self.query(
            "SELECT * FROM jobs WHERE job_title LIKE ?",
            (f"%{title}%",)
        )
    
    def query_df(self, sql, params=()):
        pd.set_option('display.max_rows', None)
        return pd.read_sql_query(sql, self.conn, params=params)
    
    def file_already_imported(self, filename: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT filename FROM files_imported WHERE filename = ?", (filename,))
        return cur.fetchone() is not None
    
    def mark_file_imported(self, filename: str):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO files_imported (filename, imported_at) VALUES (?, datetime('now'))",
            (filename,)
        )
        self.conn.commit()
    
    def close(self):
        self.conn.close()