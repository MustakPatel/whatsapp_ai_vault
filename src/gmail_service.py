import os
import re
import imaplib
import email
from email.header import decode_header
from datetime import datetime
from src.vault_service import get_setting, set_setting

def set_gmail_credentials(email_addr: str, password_or_token: str) -> dict:
    """Saves Gmail address and App Password / Token to persistent vault storage."""
    clean_email = email_addr.strip().lower()
    clean_pwd = password_or_token.strip()
    if clean_email and clean_pwd:
        set_setting("gmail_email", clean_email)
        set_setting("gmail_password", clean_pwd)
        return {"status": "success", "email": clean_email}
    return {"status": "error", "message": "Email and password cannot be empty"}

def disconnect_gmail() -> dict:
    """Removes saved Gmail credentials."""
    set_setting("gmail_email", "")
    set_setting("gmail_password", "")
    return {"status": "success", "message": "Gmail disconnected"}

def get_gmail_status() -> dict:
    """Returns current Gmail connection status."""
    email_addr = get_setting("gmail_email", os.getenv("GMAIL_EMAIL", ""))
    pwd = get_setting("gmail_password", os.getenv("GMAIL_APP_PASSWORD", ""))
    is_connected = bool(email_addr and pwd)
    return {
        "connected": is_connected,
        "email": email_addr if is_connected else "Not Connected (Demo Mode)",
        "mode": "Live Gmail IMAP" if is_connected else "Sample Demo Parser"
    }

def scan_real_gmail_imap(email_addr: str, app_password: str) -> dict:
    """Connects to Gmail IMAP via SSL, searches recent emails for bank statements, and returns parsed reports."""
    reports = []
    error_msg = None
    scanned_count = 0

    try:
        # Clean app password (remove spaces)
        clean_pwd = re.sub(r'\s+', '', app_password)
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(email_addr, clean_pwd)
        mail.select("inbox")

        # Fetch recent 30 email IDs directly for maximum reliability
        status, data = mail.search(None, "ALL")
        if status == "OK" and data[0]:
            all_ids = data[0].split()
            email_ids = all_ids[-30:] # Check top 30 most recent emails
            scanned_count = len(email_ids)

            for e_id in reversed(email_ids):
                res, msg_data = mail.fetch(e_id, "(RFC822)")
                if res == "OK":
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject = ""
                            raw_subj = msg.get("Subject", "")
                            if raw_subj:
                                decoded_seq = decode_header(raw_subj)
                                subject = "".join([
                                    t[0].decode(t[1] or "utf-8", errors="ignore") if isinstance(t[0], bytes) else str(t[0])
                                    for t in decoded_seq
                                ])
                            
                            sender = msg.get("From", "").lower()
                            body = subject + "\n"

                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() in ["text/plain", "text/html"]:
                                        try:
                                            body += part.get_payload(decode=True).decode(errors="ignore")
                                        except Exception:
                                            pass
                            else:
                                try:
                                    body += msg.get_payload(decode=True).decode(errors="ignore")
                                except Exception:
                                    pass

                            # Check if email is from a bank or contains bill keywords
                            keywords = ["bank", "card", "statement", "emi", "loan", "due", "bill", "axis", "hdfc", "icici", "sbi", "pay"]
                            if any(k in sender for k in keywords) or any(k in subject.lower() for k in keywords):
                                parsed = parse_bank_statement_text(body)
                                if parsed["total_due"] > 0:
                                    reports.append(parsed)

        mail.logout()
    except Exception as err:
        error_msg = str(err)
        print(f"IMAP Real Gmail Scan Error: {err}")

    return {
        "status": "success" if not error_msg else "error",
        "email": email_addr,
        "scanned_count": scanned_count,
        "reports": reports,
        "error": error_msg
    }

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
    """Scans Gmail inbox (Real IMAP if connected, else Demo Statements)."""
    saved_email = get_setting("gmail_email", os.getenv("GMAIL_EMAIL", ""))
    saved_password = get_setting("gmail_password", os.getenv("GMAIL_APP_PASSWORD", ""))

    if saved_email and saved_password:
        real_res = scan_real_gmail_imap(saved_email, saved_password)
        if real_res["status"] == "success":
            reports = real_res["reports"]
            if reports:
                return reports
            # If real Gmail connected successfully but no pending bills found in recent emails
            return [{
                "status": "success",
                "bank_name": f"Live Gmail ({saved_email})",
                "doc_type": "Inbox Scan Active",
                "total_due": 0.0,
                "due_date": "No Pending Bills",
                "account_suffix": "SYNCED",
                "raw_text": f"Scanned {real_res['scanned_count']} recent emails. No pending bank statements found."
            }]
        else:
            print(f"Real Gmail connection error: {real_res.get('error')}")

    # Fallback Sample Bank Emails
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
