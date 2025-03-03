from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from typing import Dict, Optional
import os

app = FastAPI()

# Serve static files (CSS, images, etc.)
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Load HTML templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Store connected users
connected_users: Dict[str, WebSocket] = {}
pairings: Dict[str, str] = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the signup page as the default homepage."""
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/chat.html", response_class=HTMLResponse)
async def chat_page(request: Request, sender: str, receiver: str):
    sender, receiver = compare_ips(sender, receiver)
    return templates.TemplateResponse("chat.html", {"request": request, "sender": sender, "receiver": receiver})

@app.websocket("/ws/{user_ip}")
async def websocket_endpoint(websocket: WebSocket, user_ip: str):
    """Handles WebSocket connections for real-time chat."""
    await websocket.accept()
    connected_users[user_ip] = websocket

    recipient_ip = find_recipient(user_ip)
    
    if recipient_ip:
        await websocket.send_text(f"✅ New Chat Session Started: {user_ip} ↔️ {recipient_ip}")
        await connected_users[recipient_ip].send_text(f"✅ New Chat Session Started: {user_ip} ↔️ {recipient_ip}")

    try:
        while True:
            data = await websocket.receive_text()

            recipient_ip = find_recipient(user_ip)

            if data == "typing...":
                if recipient_ip and recipient_ip in connected_users:
                    await connected_users[recipient_ip].send_text("typing...")
                continue

            if recipient_ip and recipient_ip in connected_users:
                await connected_users[recipient_ip].send_text(data)
            else:
                await websocket.send_text("Waiting for a chat partner...")

    except WebSocketDisconnect:
        if recipient_ip and recipient_ip in connected_users:
            await connected_users[recipient_ip].send_text(f"❌ Chat Ended: {user_ip} ↔️ {recipient_ip}")

        await handle_disconnection(user_ip)


def find_recipient(user_ip: str) -> Optional[str]:
    """Finds an available recipient for the given user."""
    for ip, ws in connected_users.items():
        if ip != user_ip and ws is not None and ip not in pairings:
            return ip
    return None

async def handle_disconnection(user_ip: str):
    """Handles user disconnection and notifies the remaining user."""
    connected_users.pop(user_ip, None)
    if user_ip in pairings:
        recipient_ip = pairings.pop(user_ip)
        if recipient_ip in pairings:
            pairings.pop(recipient_ip)
        if recipient_ip in connected_users:
            await connected_users[recipient_ip].send_text(f"User {user_ip} has disconnected. Chat ended.")


def compare_ips(sender: str, receiver: str) -> tuple:
    """Compares two IPs and assigns the smaller one as sender and the bigger one as receiver."""
    if sender > receiver:
        return receiver, sender
    return sender, receiver
