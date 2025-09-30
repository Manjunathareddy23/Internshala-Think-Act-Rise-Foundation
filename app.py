import streamlit as st
from scraper import fetch_case, fetch_causelist
from database import insert_case
import os

st.set_page_config(page_title="Court Data Fetcher", layout="centered")
st.title("Court Data Fetcher & Judgment Downloader")

# --- Fetch Case Section ---
st.header("Fetch Case Details")
case_type = st.text_input("Case Type")
case_number = st.text_input("Case Number")
year = st.text_input("Year")

if st.button("Fetch Case"):
    if not (case_type and case_number and year):
        st.error("Please enter all fields.")
    else:
        st.info("Fetching case details...")
        case_data = fetch_case(case_type, case_number, year)
        if not case_data:
            st.error("Case not found or error fetching data.")
        else:
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
    st.info("Fetching cause list...")
    causelist = fetch_causelist()
    if not causelist:
        st.error("Unable to fetch cause list. Please check the URL or your network.")
    else:
        st.success(f"{len(causelist)} cases found.")
        for c in causelist:
            st.write(f"{c['case_number']} | {c['parties']} | Next Hearing: {c['next_hearing']} | Status: {c['status']}")
