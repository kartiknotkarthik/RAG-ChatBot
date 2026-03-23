const chatWindow = document.getElementById('chat-window');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const newChatBtn = document.getElementById('btn-new-chat');
const homeBtn = document.getElementById('btn-home');
const historyList = document.getElementById('chat-history-list');

// Views
const chatView = document.getElementById('chat-view');
const homeView = document.getElementById('home-view');

// Settings Elements
const settingsModal = document.getElementById('settings-modal');
const openSettingsBtn = document.getElementById('open-settings');
const closeModalBtn = document.querySelector('.close-modal');
const themeLightBtn = document.getElementById('theme-light');
const themeDarkBtn = document.getElementById('theme-dark');

const API_URL = 'http://127.0.0.1:8000/query';

let messages = [];
let allChats = JSON.parse(localStorage.getItem('mf_chat_history') || '[]');
let currentChatId = Date.now();

// Initial Load
renderHistory();
initTheme();

// Auto-resize textarea
chatInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Send message on Enter
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

sendBtn.addEventListener('click', sendMessage);
newChatBtn.addEventListener('click', startNewChat);
homeBtn.addEventListener('click', showHome);

// Settings Handlers
openSettingsBtn.onclick = () => settingsModal.style.display = 'block';
closeModalBtn.onclick = () => settingsModal.style.display = 'none';
window.onclick = (event) => { if (event.target == settingsModal) settingsModal.style.display = 'none'; }

themeLightBtn.onclick = () =>setTheme('light');
themeDarkBtn.onclick = () => setTheme('dark');

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // 1. Add User Message
    const userMsg = { role: 'user', content: text, time: getTime() };
    messages.push(userMsg);
    renderMessage(userMsg);
    
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // 2. Add Loading
    const loadingMessageId = 'loading-' + Date.now();
    addLoadingIndicator(loadingMessageId);

    // 3. Call Backend
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: text })
        });

        const data = await response.json();
        removeLoadingIndicator(loadingMessageId);

        if (response.ok) {
            const answer = data.answer.replace(/\n/g, '<br>');
            const source = data.source;
            const sourceHtml = source.startsWith('http') 
                ? `<a href="${source}" target="_blank">${source}</a>`
                : source;
            const formattedResponse = `${answer}<br><br><small><b>Source:</b> ${sourceHtml}</small>`;
            
            const aiMsg = { role: 'ai', content: formattedResponse, time: getTime() };
            messages.push(aiMsg);
            renderMessage(aiMsg);
            
            saveCurrentChat();
        } else {
            addMessage(`Error: ${data.detail || 'Failed to get answer'}`, 'ai');
        }
    } catch (error) {
        console.error('API Error:', error);
        removeLoadingIndicator(loadingMessageId);
        addMessage(`Could not connect to backend: ${error.message}`, 'ai');
    }
}

function startNewChat() {
    showChat();
    if (messages.length > 0) {
        saveCurrentChat();
    }
    messages = [];
    currentChatId = Date.now();
    chatWindow.innerHTML = '';
    addWelcomeMessage();
    renderHistory();
}

function showHome() {
    homeView.style.display = 'block';
    chatView.style.display = 'none';
    homeBtn.classList.add('active');
    newChatBtn.classList.remove('active');
}

function showChat() {
    homeView.style.display = 'none';
    chatView.style.display = 'flex';
    newChatBtn.classList.add('active');
    homeBtn.classList.remove('active');
}

function saveCurrentChat() {
    if (messages.length === 0) return;
    
    const title = messages[0].content.substring(0, 30) + (messages[0].content.length > 30 ? '...' : '');
    const chatIndex = allChats.findIndex(c => c.id === currentChatId);
    
    if (chatIndex > -1) {
        allChats[chatIndex].messages = messages;
    } else {
        allChats.unshift({
            id: currentChatId,
            title: title,
            messages: messages,
            date: new Date().toLocaleDateString()
        });
    }
    localStorage.setItem('mf_chat_history', JSON.stringify(allChats));
    renderHistory();
}

function deleteChat(id, event) {
    event.stopPropagation();
    allChats = allChats.filter(c => c.id !== id);
    localStorage.setItem('mf_chat_history', JSON.stringify(allChats));
    if (currentChatId === id) {
        startNewChat();
    } else {
        renderHistory();
    }
}

function loadChat(id) {
    showChat();
    const chat = allChats.find(c => c.id === id);
    if (chat) {
        currentChatId = chat.id;
        messages = chat.messages;
        chatWindow.innerHTML = '';
        messages.forEach(msg => renderMessage(msg));
    }
}

function renderHistory() {
    historyList.innerHTML = '';
    allChats.forEach(chat => {
        const item = document.createElement('div');
        item.classList.add('chat-item');
        item.innerHTML = `
            <span class="material-symbols-outlined chat-icon">chat_bubble</span>
            <span class="chat-title">${chat.title}</span>
            <span class="material-symbols-outlined btn-delete-chat">close</span>
        `;
        item.querySelector('.btn-delete-chat').onclick = (e) => deleteChat(chat.id, e);
        item.onclick = () => loadChat(chat.id);
        historyList.appendChild(item);
    });
}

function renderMessage(msg) {
    const role = msg.role;
    const row = document.createElement('div');
    row.classList.add('message-row', role);

    const avatar = role === 'ai' 
        ? '<div class="ai-avatar"><span class="material-symbols-outlined">asterisk</span></div>'
        : `<div class="user-avatar"><img src="https://ui-avatars.com/api/?name=User&background=6b46c1&color=fff" alt="User"></div>`;

    const meta = role === 'ai'
        ? `<div class="message-meta">AI Assistant <span>${msg.time}</span></div>`
        : '';

    row.innerHTML = `
        ${avatar}
        <div class="message-content">
            ${meta}
            <div class="message-text">${msg.content}</div>
        </div>
    `;

    chatWindow.appendChild(row);
    scrollToBottom();
}

function addWelcomeMessage() {
    const welcome = { 
        role: 'ai', 
        content: "Hello! I am your Mutual Fund AI Assistant. I can help you with factual data about mutual funds and SEBI regulations. How can I help you today?", 
        time: getTime() 
    };
    renderMessage(welcome);
}

function addLoadingIndicator(id) {
    const row = document.createElement('div');
    row.classList.add('message-row', 'ai');
    row.id = id;
    row.innerHTML = `
        <div class="ai-avatar"><span class="material-symbols-outlined">asterisk</span></div>
        <div class="message-content">
            <div class="message-meta">AI Assistant Typing...</div>
            <div class="message-text">Thinking...<span class="dot-flashing"></span></div>
        </div>
    `;
    chatWindow.appendChild(row);
    scrollToBottom();
}

function removeLoadingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function getTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Theme Handling
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

function setTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        themeDarkBtn.classList.add('active');
        themeLightBtn.classList.remove('active');
    } else {
        document.body.classList.remove('dark-theme');
        themeLightBtn.classList.add('active');
        themeDarkBtn.classList.remove('active');
    }
    localStorage.setItem('theme', theme);
}
