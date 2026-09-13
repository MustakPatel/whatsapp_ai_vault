import os
import re
from datetime import datetime

def parse_bank_statement_text(email_body: str) -> dict:
    """Parses text from bank emails/statements and extracts due amounts, due dates, and account details."""
    result = {
        "status": "success",
        "bank_name": "Axis Bank",
        "doc_type": "Credit Card Bill",
        "total_due": 0.0,
        "due_date": "N/A",
        "account_suffix": "XXXX",
        "raw_text": email_body
    }

    # Extract Total Due
    due_match = re.search(r'(?:total\s+due|amount\s+due|total\s+payable|emi\s+amount)[:\s]+₹?\s*([\d,]+\.?\d*)', email_body, re.IGNORECASE)
    if due_match:
        val_str = due_match.group(1).replace(",", "")
        try:
            result["total_due"] = float(val_str)
        except ValueError:
            result["total_due"] = 0.0

    # Extract Due Date
    date_match = re.search(r'(?:due\s+date|payment\s+date|debit\s+date)[:\s]+([\d]{1,2}[-/\s][A-Za-z0-9]{3,8}[-/\s][\d]{2,4})', email_body, re.IGNORECASE)
    if date_match:
        result["due_date"] = date_match.group(1)
        
    # Detect Bank Name
    if "hdfc" in email_body.lower():
        result["bank_name"] = "HDFC Bank"
    elif "icici" in email_body.lower():
        result["bank_name"] = "ICICI Bank"
    elif "sbi" in email_body.lower():
        result["bank_name"] = "SBI Card"
    elif "axis" in email_body.lower():
        result["bank_name"] = "Axis Bank"

    # Detect Loan vs Credit Card
    if "loan" in email_body.lower() or "emi" in email_body.lower():
        result["doc_type"] = "Loan EMI Advice"

    return result

def scan_gmail_for_bank_statements() -> list:
    """Simulates/scans Gmail inbox for bank credit card & loan statements."""
    sample_bank_emails = [
        """
        Axis Bank Credit Card e-Statement Notice
        Dear Customer, Your Axis Bank Credit Card (Ending XX-4921) statement for August 2026 has been generated.
        Total Due: ₹14,250.00
        Minimum Amount Due: ₹1,500.00
        Payment Due Date: 22-Sep-2026
        Please ensure timely payment to avoid late charges.
        """,
        """
        Axis Bank Home Loan Repayment Advice Notice
        Dear Customer, Your Axis Bank Home Loan (Account No: LAX009812) EMI will be auto-debited.
        EMI Amount: ₹18,450.00
        Debit Date: 05-Oct-2026
        Linked Account: Axis Bank Savings Account.
        """
    ]

    parsed_reports = []
    for email in sample_bank_emails:
        parsed_reports.append(parse_bank_statement_text(email))

    return parsed_reports
