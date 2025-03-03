const sender = new URLSearchParams(window.location.search).get('sender');
const receiver = new URLSearchParams(window.location.search).get('receiver');
const websocket = new WebSocket(`ws://${window.location.host}/ws/${sender}`);

const chatArea = document.getElementById("chatArea");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const exitButton = document.getElementById("exitButton");
const chatPartner = document.getElementById("chatPartner");

// Typing Indicator Element
const typingIndicator = document.createElement("div");
typingIndicator.className = "typing";
typingIndicator.textContent = "Your chat partner is typing...";
typingIndicator.style.display = "none";
chatArea.appendChild(typingIndicator);

let typingTimeout;

chatPartner.innerHTML = `Connected to ${receiver} 💚`;

websocket.onmessage = function(event) {
    if (event.data === "typing...") {
        typingIndicator.style.display = "block";
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            typingIndicator.style.display = "none";
        }, 1000);
    } 
    else if (event.data !== "Waiting for a chat partner...") {
        const message = document.createElement("div");
        message.textContent = `${receiver}: ${event.data}`;
        message.className = "received";
        chatArea.appendChild(message);
        chatArea.scrollTop = chatArea.scrollHeight;
    }
};

sendButton.onclick = function() {
    const message = messageInput.value.trim();
    if (message !== "") {
        websocket.send(message);
        const messageDiv = document.createElement("div");
        messageDiv.textContent = `You: ${message}`;
        messageDiv.className = "sent";
        chatArea.appendChild(messageDiv);
        chatArea.scrollTop = chatArea.scrollHeight;
        messageInput.value = ""; 
    }
};

exitButton.onclick = function() {
    alert(`Disconnected from ${receiver}`);
    websocket.close();
    window.location.href = "/";
};

messageInput.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendButton.click();
    }
});

messageInput.addEventListener("input", function() {
    websocket.send("typing...");
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(() => {
        typingIndicator.style.display = "none";
    }, 1000);
});

window.onbeforeunload = function () {
    websocket.close();
};
