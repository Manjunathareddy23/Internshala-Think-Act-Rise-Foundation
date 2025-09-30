import mysql.connector

# Update with your MySQL credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Manju@12345',
    'database': 'court_db'
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def insert_case(case):
    conn = get_connection()
    cursor = conn.cursor()
    query = '''
    INSERT INTO cases 
    (case_type, case_number, year, raw_response, parties, filing_date, next_hearing, status, pdf_path)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    cursor.execute(query, (
        case['case_type'], case['case_number'], case['year'], case['raw_response'],
        case['parties'], case['filing_date'], case['next_hearing'], case['status'], case['pdf_path']
    ))
    conn.commit()
    cursor.close()
    conn.close()
