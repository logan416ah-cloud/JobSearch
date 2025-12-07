# JobSearch CLI + Data Pipeline
A Python-powered job market data extraction, cleaning, and analysis toolkit.

## Overview
JobSearch is a full-featured data pipeline that integrates with the SerpAPI Google Jobs API to:
- Search job listings across any U.S. state or all 50 states
- Save job postings as CSV datasets
- Combine, filter, and clean datasets using a dedicated processing engine
- Parse salaries into structured and annualized values
- Analyze job descriptions for keyword frequencies
- Calculate salary statistics across states or time periods
- Use a professional, multi-command CLI interface
This project turns raw job market data into actionable intelligence for researchers, analysts, and job seekers.

## Features

### Job Search
- Query job listings by state or all 50 states
- Automatic pagination handling
- Retry logic for API processing delays
- Optional CSV output

### Dataset Creation
- Combine multiple saved CSVs into unified datasets
- Filter by:
  - Job title
  - State or all states
  - Specific date (YYYY-MM-DD)
  - Year, month, or day

### Keyword Analysis
- Search job descriptions for any number of keywords
- See:
  - Total mentions
  - Per-listing frequency
  - Percentage of total results

### Salary Parsing & Statistics
- Converts salaries like:
  - 130K–160K a year
  - $30–37.50/hr
  - US$6,211–15,211/month
- Into:
  - Min, max, average
  - Annualized salary
  - Statistical summaries
