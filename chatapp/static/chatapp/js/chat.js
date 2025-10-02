// --- Multi-Chat with Markdown/Avatars UI ---
const messagesDiv = document.getElementById('messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatList = document.getElementById('chat-list');
const newChatBtn = document.getElementById('new-chat-btn');
let typingIndicator = null;
let chats = JSON.parse(localStorage.getItem('chats') || '[]');
let currentChatIdx = 0;

function saveChats() {
    localStorage.setItem('chats', JSON.stringify(chats));
    localStorage.setItem('currentChatIdx', currentChatIdx);
}

function renderChatList() {
    chatList.innerHTML = '';
    chats.forEach((chat, idx) => {
        const li = document.createElement('li');
        li.textContent = chat.name || `Chat ${idx+1}`;
        li.className = idx === currentChatIdx ? 'active' : '';
        li.onclick = () => switchChat(idx);
        // Allow renaming chat on double click
        li.ondblclick = (e) => {
            e.stopPropagation();
            const input = document.createElement('input');
            input.type = 'text';
            input.value = chat.name || `Chat ${idx+1}`;
            input.className = 'chat-rename-input';
            input.onblur = () => {
                chat.name = input.value.trim() || `Chat ${idx+1}`;
                saveChats();
                renderChatList();
            };
            input.onkeydown = (ev) => {
                if (ev.key === 'Enter') input.blur();
            };
            li.textContent = '';
            li.appendChild(input);
            input.focus();
        };
        chatList.appendChild(li);
    });
}

function switchChat(idx) {
    currentChatIdx = idx;
    saveChats();
    renderChatList();
    renderMessages();
}

function createNewChat() {
    chats.push({ name: `Chat ${chats.length+1}`, messages: [] });
    currentChatIdx = chats.length - 1;
    saveChats();
    renderChatList();
    renderMessages();
    // Auto-focus input after creating new chat
    setTimeout(() => {
        if (userInput) userInput.focus();
    }, 100);
}

function appendMessageUI(sender, text) {
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

function renderMessages() {
    messagesDiv.innerHTML = '';
    const chat = chats[currentChatIdx];
    if (!chat) return;
    chat.messages.forEach(msg => {
        appendMessageUI(msg.role, msg.content);
    });
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

newChatBtn.onclick = createNewChat;

// On page load
if (!chats.length) createNewChat();
else {
    currentChatIdx = parseInt(localStorage.getItem('currentChatIdx') || '0', 10);
    renderChatList();
    renderMessages();
}

chatForm.onsubmit = async function(e) {
    e.preventDefault();
    const userMsg = userInput.value.trim();
    if (!userMsg) return;
    chats[currentChatIdx].messages.push({ role: 'user', content: userMsg });
    saveChats();
    renderMessages();
    userInput.value = '';
    showTypingIndicator();
    try {
        const res = await fetch('/chat_api/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMsg })
        });
        const data = await res.json();
        hideTypingIndicator();
        chats[currentChatIdx].messages.push({ role: 'bot', content: data.reply });
        saveChats();
        renderMessages();
    } catch (err) {
        hideTypingIndicator();
        chats[currentChatIdx].messages.push({ role: 'bot', content: '[Error: Could not get reply]' });
        saveChats();
        renderMessages();
    }
};