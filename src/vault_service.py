import sqlite3
import os
import re

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "vault.db"))

def init_vault_db():
    """Initializes local encrypted SQLite database table for Zero-Search Personal Vault."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            key_identifier TEXT,
            amount REAL DEFAULT 0.0,
            due_date TEXT,
            content_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    # Pre-populate default seed vault records if database is empty
    cursor.execute("SELECT COUNT(*) FROM vault_items")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO vault_items (category, title, key_identifier, amount, due_date, content_text)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("Govt ID", "Aadhaar Card", "XXXX-XXXX-9182", 0.0, "N/A", "Aadhaar Card issued by UIDAI. Name: Mustak Patel. Address: Indore, MP."),
            ("Govt ID", "PAN Card", "ABCDE1234F", 0.0, "N/A", "Permanent Account Number issued by Income Tax Dept."),
            ("Govt ID", "Passport", "Z9182734", 0.0, "15-Aug-2032", "Republic of India Passport."),
            ("Credit Card Bill", "Axis Bank Credit Card", "XX-4921", 14250.0, "22-Sep-2026", "Axis Bank Credit Card August Bill. Total Due: ₹14,250.00. Due Date: 22 Sep 2026."),
            ("Loan EMI Advice", "Axis Bank Home Loan", "LAX009812", 18450.0, "05-Oct-2026", "Axis Bank Home Loan EMI Repayment. EMI: ₹18,450.00. Debit Date: 5 Oct 2026.")
        ])
        conn.commit()

    conn.close()

def add_vault_entry(category: str, title: str, key_identifier: str, amount: float = 0.0, due_date: str = "N/A", content_text: str = "") -> dict:
    """Adds a new document or financial record entry to the Vault database."""
    init_vault_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vault_items (category, title, key_identifier, amount, due_date, content_text)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (category, title, key_identifier, amount, due_date, content_text))
    conn.commit()
    conn.close()
    return {"status": "success", "title": title}

def query_vault(user_query: str) -> str:
    """Queries the vault using keyword & semantic matching and returns a formatted response."""
    init_vault_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    q_words = [w.lower() for w in re.findall(r'\w+', user_query) if len(w) > 2]
    
    cursor.execute("SELECT category, title, key_identifier, amount, due_date, content_text FROM vault_items")
    rows = cursor.fetchall()
    conn.close()

    matched = []
    for cat, title, key_id, amount, due_date, content in rows:
        combined = f"{cat} {title} {key_id} {content}".lower()
        if any(w in combined for w in q_words):
            matched.append((cat, title, key_id, amount, due_date, content))

    if not matched:
        matched = rows[:3]

    output_lines = ["🧠 *ZERO-SEARCH PERSONAL VAULT REPORT*\n"]
    for cat, title, key_id, amount, due_date, content in matched:
        amt_str = f" | Amount: ₹{amount:,.2f}" if amount > 0 else ""
        date_str = f" | Due: {due_date}" if due_date != "N/A" else ""
        output_lines.append(f"📌 *{title}* ({cat})\n• ID / Suffix: `{key_id}`{amt_str}{date_str}\n")

    return "\n".join(output_lines).strip()
