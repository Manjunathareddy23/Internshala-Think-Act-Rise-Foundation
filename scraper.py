import requests
from bs4 import BeautifulSoup
import os

PDF_FOLDER = "pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0"}

# --- Fetch individual case ---
def fetch_case(case_type, case_number, year):
    url = "https://karnatakajudiciary.kar.nic.in/case-status.asp"
    data = {
        "caseType": case_type,
        "caseNo": case_number,
        "year": year
    }
    try:
        resp = requests.post(url, headers=HEADERS, data=data, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching case:", e)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    parties = soup.select_one(".parties").text.strip() if soup.select_one(".parties") else "N/A"
    filing_date = soup.select_one(".filing-date").text.strip() if soup.select_one(".filing-date") else "N/A"
    next_hearing = soup.select_one(".next-hearing").text.strip() if soup.select_one(".next-hearing") else "N/A"
    status = soup.select_one(".status").text.strip() if soup.select_one(".status") else "N/A"

    return {
        "case_type": case_type,
        "case_number": case_number,
        "year": year,
        "parties": parties,
        "filing_date": filing_date,
        "next_hearing": next_hearing,
        "status": status,
        "raw_response": resp.text,
        "pdf_path": ""  # optional PDF download later
    }

# --- Fetch cause list (dummy local HTML file for testing) ---
def fetch_causelist():
    try:
        with open("test_causelist.html", "r") as f:
            html = f.read()
    except FileNotFoundError:
        return None

    soup = BeautifulSoup(html, 'html.parser')
    cases = []
    for row in soup.select("table tr")[1:]:
        cols = row.find_all("td")
        if len(cols) >= 4:
            cases.append({
                "case_number": cols[0].text.strip(),
                "parties": cols[1].text.strip(),
                "next_hearing": cols[2].text.strip(),
                "status": cols[3].text.strip()
            })
    return cases
