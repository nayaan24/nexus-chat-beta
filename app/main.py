from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import os
from typing import Dict, Optional

app = FastAPI() # this is initilization.

# this part imports and loads the static files(css, js, images etc.)
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# jinja templates (html pages basically)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# track online ppl.
active_users: Dict[str, WebSocket] = {}
paired_with: Dict[str, str] = {}  # who is talking to whom


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # this is setting the signup page as the default one(this will be loaded when you open the app).
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/chat.html", response_class=HTMLResponse)
async def chat_page(request: Request, sender: str, receiver: str):
    # this is the start function!this part checks which one is smaller and which one is bigger,smaller IP is set as sender and reciver ip is set as reciever.
    sender, receiver = compare_ips(sender, receiver)
    return templates.TemplateResponse(
        "chat.html", {"request": request, "sender": sender, "receiver": receiver}
    )


@app.websocket("/ws/{user_ip}")
async def chat_ws(ws: WebSocket, user_ip: str):
    # handles websocket connections for chatting..
    await ws.accept()
    active_users[user_ip] = ws

    partner_ip = grab_partner(user_ip)

    # if both users are paired, this message is shown
    if partner_ip:
        await ws.send_text(f"✅ Chat started: {user_ip} ↔️ {partner_ip}")
        await active_users[partner_ip].send_text(f"✅ Chat started: {user_ip} ↔️ {partner_ip}")

    try:
        while True:
            data = await ws.receive_text()

            partner_ip = grab_partner(user_ip)

            # a small typing indicator (took me 4 and a half days:)
            if data == "typing...":
                if partner_ip and partner_ip in active_users:
                    await active_users[partner_ip].send_text("typing...")
                continue

            # forward msg if partner is there
            if partner_ip and partner_ip in active_users:
                await active_users[partner_ip].send_text(data)
            else:
                await ws.send_text("Waiting for someone to join...")

    except WebSocketDisconnect:
        if partner_ip and partner_ip in active_users:
            await active_users[partner_ip].send_text(f"❌ Chat ended: {user_ip} ↔️ {partner_ip}")
        await clean_disconnect(user_ip)


def grab_partner(user_ip: str) -> Optional[str]:
    # a small partner finder,like it finds available and connected users,it is buggy so it is not working as i tested.
    for ip, ws in active_users.items():
        if ip != user_ip and ws is not None and ip not in paired_with:
            return ip
    return None


async def clean_disconnect(user_ip: str):
    # this function handles disconnecting
    active_users.pop(user_ip, None)
    if user_ip in paired_with:
        partner_ip = paired_with.pop(user_ip)
        if partner_ip in paired_with:
            paired_with.pop(partner_ip)
        if partner_ip in active_users:
            await active_users[partner_ip].send_text(f"user {user_ip} left. chat closed.")


def compare_ips(sender: str, receiver: str) -> tuple:
    # a small system that prevents IP collision by setting the numerically smaller IP as sender and the other one as reciever.
    if sender > receiver:
        return receiver, sender
    return sender, receiver
