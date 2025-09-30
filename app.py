import streamlit as st
from scraper import fetch_case, fetch_causelist, download_pdf
from database import insert_case
import os

st.set_page_config(page_title="Court Data Fetcher", layout="centered")
st.title("Court Data Fetcher & Judgment Downloader")

PDF_FOLDER = "pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)

# --- Select Court ---
st.header("Select Court Type")
court_type = st.radio("Court Type", options=["High Court", "District Court"])

# --- Fetch Case Section ---
st.header("Fetch Case Details")
case_type = st.text_input("Case Type")
case_number = st.text_input("Case Number")
year = st.text_input("Year")

if st.button("Fetch Case"):
    if not (case_type and case_number and year):
        st.error("Please enter all fields.")
    else:
        st.info(f"Fetching case details from {court_type}...")
        court_key = "high" if court_type.lower() == "high court" else "district"
        case_data = fetch_case(court_key, case_type, case_number, year)
        if not case_data:
            st.error("Case not found or error fetching data.")
        else:
            # Optional: download PDF if URL available
            if "pdf_url" in case_data and case_data["pdf_url"]:
                case_data['pdf_path'] = download_pdf(case_data["pdf_url"], case_number)

            insert_case(case_data)
            st.success("Case fetched successfully!")
            st.write("**Parties:**", case_data['parties'])
            st.write("**Filing Date:**", case_data['filing_date'])
            st.write("**Next Hearing:**", case_data['next_hearing'])
            st.write("**Status:**", case_data['status'])

            if case_data['pdf_path'] and os.path.exists(case_data['pdf_path']):
                st.download_button("Download Judgment PDF", case_data['pdf_path'])

# --- Fetch Cause List Section ---
st.header("Daily Cause List")
if st.button("Fetch Today's Cause List"):
    st.info(f"Fetching cause list for {court_type}...")
    court_key = "high" if court_type.lower() == "high court" else "district"
    causelist = fetch_causelist(court_key)
    if not causelist:
        st.error("Unable to fetch cause list. Please check the test HTML file.")
    else:
        st.success(f"{len(causelist)} cases found.")
        for c in causelist:
            st.write(f"{c['case_number']} | {c['parties']} | Next Hearing: {c['next_hearing']} | Status: {c['status']}")
