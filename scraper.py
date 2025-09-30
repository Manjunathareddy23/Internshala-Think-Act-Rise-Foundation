import requests
from bs4 import BeautifulSoup
import os

PDF_FOLDER = "pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0"}

# --- eCourts URLs ---
HC_BASE_URL = "https://hcservices.ecourts.gov.in/hcservices/main.php"
DC_BASE_URL = "https://services.ecourts.gov.in/ecourtindia_v6/"

# --- Fetch individual case ---
def fetch_case(court_type, case_type, case_number, year):
    """
    court_type: 'high' or 'district'
    case_type, case_number, year: strings
    """
    try:
        if court_type.lower() == "high":
            # Example endpoint for High Court (POST data may vary)
            url = HC_BASE_URL
            data = {
                "case_type": case_type,
                "case_no": case_number,
                "year": year
            }
        elif court_type.lower() == "district":
            # Example endpoint for District Court (POST data may vary)
            url = DC_BASE_URL + "case_status.php"
            data = {
                "case_type": case_type,
                "case_no": case_number,
                "year": year
            }
        else:
            print("Invalid court type")
            return None

        resp = requests.post(url, headers=HEADERS, data=data, timeout=10)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("Error fetching case:", e)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    # Parsing logic may vary based on actual eCourts HTML
    parties = soup.select_one(".parties").text.strip() if soup.select_one(".parties") else "N/A"
    filing_date = soup.select_one(".filing-date").text.strip() if soup.select_one(".filing-date") else "N/A"
    next_hearing = soup.select_one(".next-hearing").text.strip() if soup.select_one(".next-hearing") else "N/A"
    status = soup.select_one(".status").text.strip() if soup.select_one(".status") else "N/A"

    return {
        "court_type": court_type,
        "case_type": case_type,
        "case_number": case_number,
        "year": year,
        "parties": parties,
        "filing_date": filing_date,
        "next_hearing": next_hearing,
        "status": status,
        "raw_response": resp.text,
        "pdf_path": ""  # optional: add PDF download logic
    }

# --- Fetch cause list (dummy local HTML fallback for testing) ---
def fetch_causelist(court_type="high"):
    """
    Returns a list of cause list cases.
    For testing, uses local HTML file.
    """
    # In real implementation, fetch from eCourts URLs:
    # HC: HC_BASE_URL + "daily_cause_list.php"
    # DC: DC_BASE_URL + "daily_cause_list.php"
    
    try:
        filename = "test_causelist.html"  # local fallback
        with open(filename, "r") as f:
            html = f.read()
    except FileNotFoundError:
        print("Cause list HTML file not found.")
        return []

    soup = BeautifulSoup(html, "html.parser")
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

# --- Optional: function to download judgment PDF ---
def download_pdf(pdf_url, case_number):
    """
    pdf_url: link to judgment PDF
    case_number: used for saving file
    """
    if not pdf_url:
        return ""
    try:
        resp = requests.get(pdf_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        file_path = os.path.join(PDF_FOLDER, f"{case_number}.pdf")
        with open(file_path, "wb") as f:
            f.write(resp.content)
        return file_path
    except Exception as e:
        print("Error downloading PDF:", e)
        return ""
