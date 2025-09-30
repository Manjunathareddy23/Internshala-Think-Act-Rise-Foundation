import requests
from bs4 import BeautifulSoup
import os

PDF_FOLDER = "pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# --- Fetch Case Details ---
def fetch_case(case_type, case_number, year):
    url = f"https://karnatakajudiciary.kar.nic.in/case-status.asp?caseType={case_type}&caseNo={case_number}&year={year}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching case:", e)
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')

    parties = soup.select_one(".parties").text.strip() if soup.select_one(".parties") else "N/A"
    filing_date = soup.select_one(".filing-date").text.strip() if soup.select_one(".filing-date") else "N/A"
    next_hearing = soup.select_one(".next-hearing").text.strip() if soup.select_one(".next-hearing") else "N/A"
    status = soup.select_one(".status").text.strip() if soup.select_one(".status") else "N/A"

    # Download PDF
    pdf_link = soup.select_one(".judgment-link")["href"] if soup.select_one(".judgment-link") else None
    pdf_path = ""
    if pdf_link:
        try:
            pdf_resp = requests.get(pdf_link, headers=HEADERS, timeout=10)
            pdf_path = os.path.join(PDF_FOLDER, f"{case_number}_{year}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_resp.content)
        except requests.exceptions.RequestException:
            pdf_path = ""

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
    url = "https://example-ecourts.gov.in/causelist/today"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching cause list:", e)
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    cases = []
    for row in soup.select("table tr")[1:]:  # skip header
        cols = row.find_all("td")
        if len(cols) >= 4:
            cases.append({
                "case_number": cols[0].text.strip(),
                "parties": cols[1].text.strip(),
                "next_hearing": cols[2].text.strip(),
                "status": cols[3].text.strip()
            })
    return cases
