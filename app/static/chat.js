// This part extracts the sender and receiver from the URL
let senderName = new URLSearchParams(window.location.search).get('sender');
let recvName = new URLSearchParams(window.location.search).get('receiver');

// this is the websocket setup
let ws = new WebSocket(`wss://${window.location.host}/ws/${senderName}`);

// DOM,that is:referencing/connecting html/css to javascript
let chatBox = document.getElementById("chatArea");
let msgInput = document.getElementById("messageInput");
let sendBtn = document.getElementById("sendButton");
let exitBtn = document.getElementById("exitButton");
let partnerLabel = document.getElementById("chatPartner");

// typing indicator system...
let typingDiv = document.createElement("div");
typingDiv.className = "typing";
typingDiv.textContent = "Your chat partner is typing...";
typingDiv.style.display = "none";
chatBox.appendChild(typingDiv);

let typingTimer; // debug: to hide typing status

partnerLabel.innerHTML = `Connected to ${recvName} 💚`;

// incoming messages
ws.onmessage = function(evt) {
    console.log("debug: got msg ->", evt.data);

    if (evt.data === "typing...") {
        typingDiv.style.display = "block";
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => {
            typingDiv.style.display = "none";
        }, 1000);
    } else if (evt.data !== "Waiting for a chat partner...") {
        let msgDiv = document.createElement("div");
        msgDiv.textContent = `${recvName}: ${evt.data}`;
        msgDiv.className = "received";
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
};

// sending messages
sendBtn.onclick = function() {
    let text = msgInput.value.trim();

    if (text.length > 0) {
        ws.send(text);

        let sentDiv = document.createElement("div");
        sentDiv.textContent = `You: ${text}`;
        sentDiv.className = "sent";
        chatBox.appendChild(sentDiv);

        chatBox.scrollTop = chatBox.scrollHeight;
        msgInput.value = ""; // clear box
    } else {
        console.log("debug: empty message not sent");
    }
};

// exit button functioning
exitBtn.onclick = function() {
    alert(`Disconnected from ${recvName}`);
    try {
        ws.close();
    } catch (err) {
        console.log("debug: ws already closed?", err);
    }
    window.location.href = "/";
};

// pressing Enter sends mesg
msgInput.addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        sendBtn.click();
    }
});

// typing event
msgInput.addEventListener("input", function() {
    ws.send("typing...");
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => {
        typingDiv.style.display = "none";
    }, 1000);
});

// this part closes the websocket connection if the page is closed..
window.onbeforeunload = function() {
    ws.close();
};
