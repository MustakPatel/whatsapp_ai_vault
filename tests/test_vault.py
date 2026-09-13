import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.vault_service import query_vault, add_vault_entry

def test_query_vault_structure():
    res = query_vault("PAN Card Number")
    assert isinstance(res, str)
    assert "ZERO-SEARCH PERSONAL VAULT REPORT" in res
    assert "PAN Card" in res

def test_add_vault_entry():
    entry = add_vault_entry("Insurance", "HDFC ERGO Health Insurance", "POL-91827", 12500.0, "10-Oct-2026", "Health Insurance Policy")
    assert entry["status"] == "success"
    res = query_vault("Health Insurance")
    assert "HDFC ERGO" in res
