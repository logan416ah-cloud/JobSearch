# from jobsearch import Clean
from database import Database

# db = Database()

# results = db.query("SELECT * FROM jobs WHERE job_title LIKE ?", ("%cyber%",))
# # results = db.get_jobs_by_title("Cybersecurity")

# for row in results:
#     print(row)

# db.close()

db = Database()

df = db.query_df("""
    SELECT job_title, company, state, min_annualized, max_annualized
    FROM jobs
    WHERE state = ?
    ORDER BY max_annualized DESC
""", ("California",))

print(df)
db.close()


# c = Clean()
# c.import_csv_folder_to_db()
