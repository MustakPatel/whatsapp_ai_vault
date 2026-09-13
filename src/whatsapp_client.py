import os
import requests

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "EAAX_SANDBOX_MOCK_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "100200300400")
GRAPH_API_VERSION = "v19.0"

def send_whatsapp_message(to_phone: str, text_body: str) -> bool:
    """Sends a text message to a user via Meta WhatsApp Cloud API."""
    if not WHATSAPP_TOKEN or WHATSAPP_TOKEN.startswith("EAAX_SANDBOX_MOCK"):
        print(f"📱 [MOCK WHATSAPP OUTBOUND to {to_phone}]:\n{text_body}")
        return True

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {"preview_url": False, "body": text_body}
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"WhatsApp API Status: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return False

def send_whatsapp_document(to_phone: str, document_url: str, filename: str, caption: str = "") -> bool:
    """Sends a PDF or media document link to a user via WhatsApp Cloud API."""
    if not WHATSAPP_TOKEN or WHATSAPP_TOKEN.startswith("EAAX_SANDBOX_MOCK"):
        print(f"📄 [MOCK WHATSAPP DOCUMENT to {to_phone}]: {filename} ({document_url}) - {caption}")
        return True

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "document",
        "document": {
            "link": document_url,
            "filename": filename,
            "caption": caption
        }
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        return r.status_code == 200
    except Exception as e:
        print(f"Error sending WhatsApp document: {e}")
        return False

def send_whatsapp_quick_buttons(to_phone: str, text_body: str, button_titles: list) -> bool:
    """Sends interactive quick-reply buttons to user in WhatsApp."""
    if not WHATSAPP_TOKEN or WHATSAPP_TOKEN.startswith("EAAX_SANDBOX_MOCK"):
        print(f"🔘 [MOCK WHATSAPP BUTTONS to {to_phone}]: {text_body} | Buttons: {button_titles}")
        return True

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    buttons = []
    for idx, title in enumerate(button_titles[:3]):
        buttons.append({
            "type": "reply",
            "reply": {
                "id": f"btn_{idx}",
                "title": title[:20]
            }
        })

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text_body},
            "action": {"buttons": buttons}
        }
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=15)
        return r.status_code == 200
    except Exception as e:
        print(f"Error sending WhatsApp buttons: {e}")
        return False
