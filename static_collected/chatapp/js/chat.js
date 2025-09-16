const messagesDiv = document.getElementById('messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
let typingIndicator = null;

function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);

    // Avatar
    const avatar = document.createElement('div');
    avatar.classList.add('avatar');
    avatar.innerHTML = sender === 'user' ? '' : '';
    msgDiv.appendChild(avatar);

    // Bubble with markdown support
    const bubble = document.createElement('div');
    bubble.classList.add('bubble');
    bubble.innerHTML = window.marked && marked.parseInline ? marked.parseInline(text) : text;
    msgDiv.appendChild(bubble);

    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showTypingIndicator() {
    typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator bot';
    typingIndicator.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
    messagesDiv.appendChild(typingIndicator);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function hideTypingIndicator() {
    if (typingIndicator) {
        messagesDiv.removeChild(typingIndicator);
        typingIndicator = null;
    }
}

chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;
    appendMessage('user', text);
    userInput.value = '';
    showTypingIndicator();
    // Send user message to Django API
    fetch('/api/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        if (data.reply) {
            appendMessage('bot', data.reply);
        } else {
            appendMessage('bot', 'Sorry, there was an error.');
        }
    })
    .catch(() => {
        hideTypingIndicator();
        appendMessage('bot', 'Sorry, there was an error.');
    });
});