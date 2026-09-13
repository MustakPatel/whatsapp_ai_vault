import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.gmail_service import parse_bank_statement_text, scan_gmail_for_bank_statements

def test_parse_bank_statement_text():
    sample = "Axis Bank Credit Card e-Statement. Total Due: ₹14,250.00. Payment Due Date: 22-Sep-2026."
    res = parse_bank_statement_text(sample)
    assert res["status"] == "success"
    assert res["bank_name"] == "Axis Bank"
    assert res["total_due"] == 14250.0
    assert "22-Sep-2026" in res["due_date"]

def test_scan_gmail_for_bank_statements():
    statements = scan_gmail_for_bank_statements()
    assert isinstance(statements, list)
    assert len(statements) >= 2
