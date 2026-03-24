
from flask import Flask, render_template_string, request
import asyncio
import threading
import os
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH"))
phone = os.getenv("PHONE")

target_chat = int(os.getenv("TARGET_CHAT"))
delay = int(os.getenv("DELAY", 2))

sources = []
running = False

client = TelegramClient("session", api_id, api_hash)

HTML = '''
<h2>Telegram Forwarder Dashboard (Online)</h2>
<form method="post">
Add Source: <input name="source">
<button>Add</button>
</form>

<h3>Sources</h3>
<ul>
{% for s in sources %}
<li>{{s}}</li>
{% endfor %}
</ul>

<form method="post">
<button name="start">Start</button>
<button name="stop">Stop</button>
</form>

<p>Status: {{status}}</p>
'''

@app.route("/", methods=["GET","POST"])
def index():
    global running
    if request.method == "POST":
        if "source" in request.form:
            sources.append(request.form["source"])
        if "start" in request.form:
            start_bot()
        if "stop" in request.form:
            running = False
    return render_template_string(HTML, sources=sources, status=running)

def start_bot():
    global running
    if running:
        return
    running = True
    threading.Thread(target=run_bot).start()

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    @client.on(events.NewMessage(chats=sources))
    async def handler(event):
        if not running:
            return
        await asyncio.sleep(delay)
        await client.send_message(target_chat, event.message.message or "", file=event.message.media)

    async def main():
        await client.start(phone)
        await client.run_until_disconnected()

    loop.run_until_complete(main())

if __name__ == "__main__":
    # Railway assigns PORT automatically
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
