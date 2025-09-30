import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

PDF_FOLDER = "pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)

# --- Fetch Case Details ---
def fetch_case(case_type, case_number, year):
    # Replace this with actual eCourts URL
    url = f"https://example-ecourts.gov.in/case?type={case_type}&number={case_number}&year={year}"
    
    resp = requests.get(url)
    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Example selectors — replace with actual ones
    parties = soup.select_one(".parties").text.strip() if soup.select_one(".parties") else "N/A"
    filing_date = soup.select_one(".filing-date").text.strip() if soup.select_one(".filing-date") else "N/A"
    next_hearing = soup.select_one(".next-hearing").text.strip() if soup.select_one(".next-hearing") else "N/A"
    status = soup.select_one(".status").text.strip() if soup.select_one(".status") else "N/A"
    
    # Download PDF judgment
    pdf_link = soup.select_one(".judgment-link")["href"] if soup.select_one(".judgment-link") else None
    pdf_path = ""
    if pdf_link:
        pdf_resp = requests.get(pdf_link)
        pdf_path = os.path.join(PDF_FOLDER, f"{case_number}_{year}.pdf")
        with open(pdf_path, "wb") as f:
            f.write(pdf_resp.content)

    return {
        "case_type": case_type,
        "case_number": case_number,
        "year": year,
        "raw_response": resp.text,
        "parties": parties,
        "filing_date": filing_date,
        "next_hearing": next_hearing,
        "status": status,
        "pdf_path": pdf_path
    }

# --- Fetch Cause List ---
def fetch_causelist(court_code=None):
    # Example: Daily cause list URL
    url = "https://example-ecourts.gov.in/causelist/today"
    
    resp = requests.get(url)
    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    cases = []
    for row in soup.select("table tr")[1:]:  # skip header
        cols = row.find_all("td")
        if len(cols) >= 4:
            case_number = cols[0].text.strip()
            parties = cols[1].text.strip()
            next_hearing = cols[2].text.strip()
            status = cols[3].text.strip()
            cases.append({
                "case_number": case_number,
                "parties": parties,
                "next_hearing": next_hearing,
                "status": status
            })
    return cases
