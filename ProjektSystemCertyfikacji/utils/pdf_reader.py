from pypdf import PdfReader
import re
from datetime import datetime

def extract_data(certificate_file):
    data = {}

    reader = PdfReader(certificate_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    cert_number = re.search(r'I\.1 Numer dokumentu\s*(.+)', text)
    if cert_number:
        data['certificate_number'] = cert_number.group(1).strip()

    sub_type = re.search(r'I\.2 Rodzaj podmiotu\s*(.+)', text)
    if sub_type:
        line = sub_type.group(1).strip()
        if '☑ Podmiot' in line:
            data['subject_type'] = 'subject'
        else:
            data['subject_type'] = 'group_of_subjects'

    holder_company_name = re.search(r'I\.3 Podmiot lub grupa podmiotów.*?Nazwa(.*?)Adres', text, re.DOTALL)
    if holder_company_name:
        data['holder_company_name'] = holder_company_name.group(1).strip()

    issued_by_certifying_unit_id = re.search(r'I\.4 Właściwy organ.*?Organ(.*?)Adres', text, re.DOTALL)
    if issued_by_certifying_unit_id:
        data['issued_by_certifying_unit_name'] = issued_by_certifying_unit_id.group(1).strip()

    valid_from_to = re.search(r'Certyfikat ważny od dnia (\d{2}/\d{2}/\d{4}) do dnia (\d{2}/\d{2}/\d{4})', text)
    if valid_from_to:
        data['valid_from'] = datetime.strptime(valid_from_to.group(1), '%d/%m/%Y').date()
        data['valid_to'] = datetime.strptime(valid_from_to.group(2), '%d/%m/%Y').date()

    activity_areas = re.search(r'I\.5 Działalność podmiotu.*?\n(.*?)(?=\nI\.|\Z)', text, re.DOTALL)
    if activity_areas:
        areas = re.findall(r'•\s*(.+)', activity_areas.group(1))
        data['activity_areas'] = [a.strip() for a in areas]
    else:
        data['activity_areas'] = []
    # print("Znalezione activity areas:", data['activity_areas'])

    return data