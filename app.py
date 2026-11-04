import os, requests
from flask import Flask, request

app = Flask(__name__)
VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]
WA_TOKEN = os.environ["WA_TOKEN"]
PHONE_ID = os.environ["PHONE_ID"]
AI_KEY = os.environ["ANTHROPIC_API_KEY"]

def ask_ai(text):
    r = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent",
        headers={"x-goog-api-key": AI_KEY},
        json={"contents": [{"parts": [{"text": text}]}]},
        timeout=30)
    try:
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return "Mwen pa ka reponn kounye a, eseye ankò."

def send(to, text):
    requests.post(
        f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages",
        headers={"Authorization": f"Bearer {WA_TOKEN}"},
        json={"messaging_product": "whatsapp", "to": to,
              "text": {"body": text}})

@app.get("/webhook")
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Erreur", 403

@app.post("/webhook")
def receive():
    data = request.get_json()
    try:
        msg = data["entry"][0]["changes"][0]["value"]["messages"][0]
        if msg["type"] == "text":
            send(msg["from"], ask_ai(msg["text"]["body"]))
    except (KeyError, IndexError):
        pass
    return "ok", 200
