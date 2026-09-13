from flask import Flask, request, jsonify
import os
import sys
import threading
import time
import requests

# Ensure root directory is in sys.path
root_dir = os.path.abspath(os.path.dirname(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.whatsapp_client import send_whatsapp_message, send_whatsapp_quick_buttons
from src.gmail_service import scan_gmail_for_bank_statements
from src.vahan_service import get_vehicle_details
from src.vault_service import query_vault, init_vault_db

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "WHATSAPP_VAULT_SECRET_VERIFY_TOKEN")
PORT = int(os.getenv("PORT", 5000))

# Initialize database on startup
init_vault_db()

@app.route("/")
def index():
    return jsonify({
        "status": "active",
        "service": "Meta WhatsApp AI Executive Assistant & Personal Vault",
        "author": "Antigravity AI"
    })

@app.route("/health")
def health():
    return "OK", 200

@app.route("/chat")
@app.route("/simulate", methods=["GET", "POST"])
def simulate_whatsapp_chat():
    """Simulates WhatsApp AI Assistant chat query via Web Interface / HTTP without requiring Meta Developer login."""
    # Check if request wants JSON or HTML UI
    is_json = request.is_json or request.headers.get("Accept", "").startswith("application/json") or request.args.get("format") == "json"

    if request.method == "POST":
        data = request.get_json() or request.form or {}
        msg_text = data.get("message", data.get("Body", "hi"))
    else:
        msg_text = request.args.get("message", "")

    # If GET without message parameter, serve beautiful WhatsApp Web Chat UI
    if request.method == "GET" and not msg_text and not is_json:
        return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WhatsApp AI Vault & Executive Assistant</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: #0b141a; color: #e9edef; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        .header { background: #202c33; padding: 14px 20px; display: flex; align-items: center; gap: 14px; border-bottom: 1px solid #222d34; }
        .avatar { width: 44px; height: 44px; border-radius: 50%; background: #00a884; display: flex; align-items: center; justify-content: center; font-size: 22px; }
        .title-area h2 { font-size: 16px; font-weight: 600; color: #e9edef; }
        .title-area p { font-size: 12px; color: #00a884; font-weight: 500; }
        .chat-box { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; background: #0b141a; }
        .msg { max-width: 80%; padding: 12px 16px; border-radius: 12px; font-size: 14.5px; line-height: 1.5; white-space: pre-wrap; word-break: break-word; }
        .msg.bot { background: #202c33; align-self: flex-start; border-top-left-radius: 2px; color: #e9edef; }
        .msg.user { background: #005c4b; align-self: flex-end; border-top-right-radius: 2px; color: #e9edef; }
        .chips { display: flex; gap: 8px; flex-wrap: wrap; padding: 10px 20px; background: #111b21; border-top: 1px solid #222d34; }
        .chip { background: #202c33; color: #00a884; border: 1px solid #222d34; padding: 6px 14px; border-radius: 18px; font-size: 13px; cursor: pointer; transition: 0.2s; font-weight: 500; }
        .chip:hover { background: #00a884; color: #111b21; }
        .input-area { background: #202c33; padding: 12px 20px; display: flex; gap: 12px; align-items: center; }
        input { flex: 1; background: #2a3942; border: none; padding: 12px 18px; border-radius: 8px; color: #e9edef; font-size: 15px; outline: none; }
        button { background: #00a884; color: #111b21; border: none; padding: 12px 24px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 15px; }
        button:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <div class="header">
        <div class="avatar">🤖</div>
        <div class="title-area">
            <h2>WhatsApp AI Assistant & Personal Vault</h2>
            <p>● Online 24/7 (Zero-Search Vault Active)</p>
        </div>
    </div>
    <div class="chat-box" id="chat">
        <div class="msg bot">🟢 <b>WHATSAPP AI EXECUTIVE ASSISTANT</b> 🟢\n\n📲 <b>Try these instant live commands:</b>\n• Type <b>bills</b> for Bank Credit Card & Loan EMI Notices\n• Type <b>vehicle MP09XX1234</b> for Parivahan Vehicle Info\n• Ask any query like <b>Mera PAN card number kya hai?</b></div>
    </div>
    <div class="chips">
        <div class="chip" onclick="sendMsg('bills')">💳 Bank Bills & Loan EMI</div>
        <div class="chip" onclick="sendMsg('vehicle MP09XX1234')">🚗 Vehicle RC & Insurance</div>
        <div class="chip" onclick="sendMsg('Mera PAN card number kya hai?')">🧠 Search PAN / Aadhaar</div>
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Type a message or command..." onkeypress="if(event.key==='Enter') sendUserMsg()">
        <button onclick="sendUserMsg()">Send</button>
    </div>
    <script>
        function appendMsg(text, type) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'msg ' + type;
            div.innerHTML = text.replace(/\\n/g, '<br>').replace(/\*(.*?)\*/g, '<b>$1</b>').replace(/`(.*?)`/g, '<code>$1</code>');
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        function sendMsg(text) {
            appendMsg(text, 'user');
            fetch('/simulate?format=json&message=' + encodeURIComponent(text))
                .then(r => r.json())
                .then(d => appendMsg(d.response, 'bot'))
                .catch(e => appendMsg('⚠️ Connection error.', 'bot'));
        }
        function sendUserMsg() {
            const input = document.getElementById('userInput');
            if (input.value.trim()) {
                sendMsg(input.value.trim());
                input.value = '';
            }
        }
    </script>
</body>
</html>"""

    text_strip = msg_text.strip() if msg_text else "hi"
    cmd = text_strip.lower()

    if cmd in ["hi", "hello", "help", "/start"]:
        reply = """
🟢 *WHATSAPP AI EXECUTIVE ASSISTANT & PERSONAL VAULT* 🟢

📲 *Available Commands:*
• 💳 *Type 'bills' or 'gmail':* Auto-fetch Credit Card bills & Loan EMI notices
• 🚗 *Type 'vehicle MP09XX1234':* Instant Parivahan Vehicle RC, Insurance & Pollution status
• 🧠 *Type any question:* Zero-search query (e.g. _'Mera PAN card number kya hai?'_ or _'Axis Bank bill कितना baki hai?'_)
"""
    elif cmd in ["bills", "gmail", "emi"]:
        statements = scan_gmail_for_bank_statements()
        reply = "💳 *LATEST BANK & LOAN STATEMENTS*\n\n"
        for st in statements:
            reply += f"📌 *{st['bank_name']}* ({st['doc_type']})\n💰 Total Due: ₹{st['total_due']:,.2f}\n⏰ Due Date: {st['due_date']}\n\n"
    elif cmd.startswith("vehicle"):
        parts = text_strip.split()
        reg_no = parts[1] if len(parts) > 1 else "MP09XX1234"
        info = get_vehicle_details(reg_no)
        if info["status"] == "success":
            reply = f"""
🚗 *PARIVAHAN VEHICLE DETAILS REPORT* 🚗

📌 *Reg No:* `{info['registration_no']}`
👤 *Owner Name:* {info['owner_name']}
🚘 *Model:* {info['maker_model']}
📅 *Reg Date:* {info['registration_date']}
🛡️ *Insurance Valid Upto:* {info['insurance_valid_upto']} ({info['insurance_company']})
🍃 *Pollution (PUCC) Expiry:* {info['pucc_valid_upto']}
"""
        else:
            reply = f"⚠️ Error fetching vehicle details for {reg_no}"
    else:
        reply = query_vault(text_strip)

    if is_json:
        return jsonify({"status": "success", "message": text_strip, "response": reply.strip()})
    return reply.replace('\n', '<br>')

@app.route("/webhook", methods=["GET"])
def webhook_verification():
    """Meta WhatsApp Cloud API Webhook verification challenge handler."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK_VERIFIED by Meta!")
        return challenge, 200
    else:
        print("Webhook verification failed. Token mismatch.")
        return "Forbidden", 403

def process_inbound_whatsapp_message(sender_phone: str, text: str):
    """Processes incoming WhatsApp messages from Meta Webhook."""
    text_strip = text.strip()
    cmd = text_strip.lower()

    if cmd in ["hi", "hello", "help", "/start"]:
        msg = """
🟢 *META WHATSAPP AI EXECUTIVE ASSISTANT* 🟢

📲 *Available WhatsApp Commands:*
• 💳 *Type 'bills' or 'gmail':* Auto-fetch Credit Card bills & Loan EMI notices
• 🚗 *Type 'vehicle MP09XX1234':* Instant Parivahan Vehicle RC, Insurance & Pollution status
• 🧠 *Type any question:* Zero-search query (e.g. _'Mera PAN card number kya hai?'_ or _'Axis Bank bill कितना baki hai?'_)
"""
        send_whatsapp_quick_buttons(sender_phone, msg.strip(), ["Bills & EMI", "Vehicle Info", "Vault Search"])
        return

    elif cmd in ["bills", "gmail", "emi"]:
        statements = scan_gmail_for_bank_statements()
        msg = "💳 *LATEST BANK & LOAN STATEMENTS*\n\n"
        for st in statements:
            msg += f"📌 *{st['bank_name']}* ({st['doc_type']})\n💰 Total Due: ₹{st['total_due']:,.2f}\n⏰ Due Date: {st['due_date']}\n\n"
        send_whatsapp_message(sender_phone, msg.strip())
        return

    elif cmd.startswith("vehicle"):
        parts = text_strip.split()
        reg_no = parts[1] if len(parts) > 1 else "MP09XX1234"
        info = get_vehicle_details(reg_no)
        if info["status"] == "success":
            msg = f"""
🚗 *PARIVAHAN VEHICLE DETAILS REPORT* 🚗

📌 *Reg No:* `{info['registration_no']}`
👤 *Owner Name:* {info['owner_name']}
🚘 *Model:* {info['maker_model']}
📅 *Reg Date:* {info['registration_date']}
🛡️ *Insurance Valid Upto:* {info['insurance_valid_upto']} ({info['insurance_company']})
🍃 *Pollution (PUCC) Expiry:* {info['pucc_valid_upto']}
"""
            send_whatsapp_message(sender_phone, msg.strip())
        else:
            send_whatsapp_message(sender_phone, f"⚠️ Error fetching vehicle details for {reg_no}")
        return

    else:
        # Search Zero-Search Vault
        reply = query_vault(text_strip)
        send_whatsapp_message(sender_phone, reply)

@app.route("/webhook", methods=["POST"])
def webhook_inbound():
    """Meta WhatsApp Cloud API inbound message receiver."""
    body = request.get_json() or {}
    try:
        entries = body.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    sender_phone = msg.get("from", "")
                    msg_type = msg.get("type", "")
                    text_content = ""

                    if msg_type == "text":
                        text_content = msg.get("text", {}).get("body", "")
                    elif msg_type == "interactive":
                        text_content = msg.get("interactive", {}).get("button_reply", {}).get("title", "")

                    if sender_phone and text_content:
                        print(f"Received WhatsApp message from {sender_phone}: '{text_content}'")
                        t = threading.Thread(
                            target=process_inbound_whatsapp_message,
                            args=(sender_phone, text_content),
                            daemon=True
                        )
                        t.start()
    except Exception as e:
        print(f"Error parsing WhatsApp webhook payload: {e}")

    return "EVENT_RECEIVED", 200

def keep_alive_ping_worker():
    """Pings public URL every 8 minutes to prevent Render Free Tier sleep."""
    public_url = os.environ.get("RENDER_EXTERNAL_URL", f"http://localhost:{PORT}")
    print(f"💓 Keep-Alive Worker initialized for {public_url}")
    while True:
        time.sleep(480) # 8 minutes
        try:
            r = requests.get(f"{public_url.rstrip('/')}/health", timeout=15)
            print(f"💓 Keep-Alive Ping Status: {r.status_code}")
        except Exception as e:
            print(f"Keep-Alive ping error: {e}")

# Launch Keep-Alive Thread
try:
    ka_thread = threading.Thread(target=keep_alive_ping_worker, daemon=True)
    ka_thread.start()
except Exception as e:
    print(f"Error starting keep-alive thread: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
