import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
from bs4 import BeautifulSoup

PDF_FOLDER = "pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)

# --- Fetch Case Details (unchanged, using requests for specific case) ---
HEADERS = {"User-Agent": "Mozilla/5.0"}

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
        "pdf_path": ""
    }

# --- Fetch Cause List using Selenium ---
def fetch_causelist():
    # Configure headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service("/path/to/chromedriver")  # <-- REPLACE with your chromedriver path
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://karnatakajudiciary.kar.nic.in/dailycause-list.asp"
    try:
        driver.get(url)
        time.sleep(5)  # wait for page to load
        cases = []
        rows = driver.find_elements(By.XPATH, "//table//tr")[1:]  # skip header
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 4:
                cases.append({
                    "case_number": cols[0].text.strip(),
                    "parties": cols[1].text.strip(),
                    "next_hearing": cols[2].text.strip(),
                    "status": cols[3].text.strip()
                })
    except Exception as e:
        print("Error fetching cause list:", e)
        cases = []
    finally:
        driver.quit()

    return cases
