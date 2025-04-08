# NAD Web App – Crawling & Artistic Website Analysis

This Streamlit app is a research tool for analyzing websites based on artistic and conventional design features.  
It was developed as part of the *NAD* project to help explore the aesthetics and structures of web pages.

---

## What it does

You can choose between two modes:

### Crawl the Web *(coming soon)*
Provide a starting URL and a crawl depth. The app will eventually crawl and collect linked pages from that starting point.

### Analyze a List of URLs
Paste in one or more website URLs (one per line), and the app will:
- Fetch the HTML of each site
- Analyze it for artistic and conventional elements
- Output the score and detected features
- Allow you to download a structured JSON report

---

## How to run it locally

You need Python 3 and the packages listed in `requirements.txt`.  
Once installed, run:

```bash
streamlit run web_app_01.py