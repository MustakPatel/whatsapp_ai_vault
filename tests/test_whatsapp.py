import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.whatsapp_client import send_whatsapp_message, send_whatsapp_document, send_whatsapp_quick_buttons
from app import app

def test_send_whatsapp_message():
    assert send_whatsapp_message("919876543210", "Hello Test") is True

def test_send_whatsapp_document():
    assert send_whatsapp_document("919876543210", "https://example.com/test.pdf", "test.pdf", "Caption") is True

def test_send_whatsapp_quick_buttons():
    assert send_whatsapp_quick_buttons("919876543210", "Select option", ["Option 1", "Option 2"]) is True

def test_app_webhook_get():
    client = app.test_client()
    resp = client.get("/webhook?hub.mode=subscribe&hub.verify_token=WHATSAPP_VAULT_SECRET_VERIFY_TOKEN&hub.challenge=12345")
    assert resp.status_code == 200
    assert resp.data.decode("utf-8") == "12345"
