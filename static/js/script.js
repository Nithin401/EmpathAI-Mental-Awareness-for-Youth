const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const moodDisplay = document.getElementById('mood-display');
const recommendationArea = document.getElementById('recommendation-area');
const spinner = document.getElementById('spinner');

let moodHistory = [];

function displayMessage(sender, message) {
    const messageRow = document.createElement('div');
    messageRow.classList.add('message-row', sender === 'user' ? 'user-row' : 'bot-row');

    const messageBubble = document.createElement('div');
    messageBubble.classList.add('message-bubble', sender === 'user' ? 'user-message' : 'bot-message');
    messageBubble.textContent = message;

    if (sender === 'user') {
        messageRow.appendChild(messageBubble);
        const avatar = document.createElement('img');
        avatar.src = 'https://via.placeholder.com/35/007bff/FFFFFF?text=YOU'; // Placeholder for user avatar
        avatar.classList.add('message-avatar');
        messageRow.appendChild(avatar);
    } else {
        const avatar = document.createElement('img');
        avatar.src = 'https://via.placeholder.com/35/28a745/FFFFFF?text=AI'; // Placeholder for bot avatar
        avatar.classList.add('message-avatar');
        messageRow.appendChild(avatar);
        messageRow.appendChild(messageBubble);
    }

    chatBox.appendChild(messageRow);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function updateMoodDisplay(mood) {
    const moodEmojis = {
        'POSITIVE': '😊',
        'NEGATIVE': '😔',
        'NEUTRAL': '😐'
    };
    moodDisplay.textContent = `Current Mood: ${moodEmojis[mood]}`;

    moodHistory.push(mood);
    if (moodHistory.length > 5) {
        moodHistory.shift();
    }

    const negativeCount = moodHistory.filter(m => m === 'NEGATIVE').length;
    if (negativeCount >= 3) {
        recommendationArea.classList.remove('d-none');
    } else {
        recommendationArea.classList.add('d-none');
    }
}

async function sendMessage() {
    const userMessage = messageInput.value.trim();
    if (userMessage === '') return;

    displayMessage('user', userMessage);
    messageInput.value = '';

    // Show spinner and disable input/button during loading
    spinner.style.display = 'block';
    sendButton.disabled = true;
    messageInput.disabled = false;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: userMessage })
        });

        const data = await response.json();
        if (data.error) {
            displayMessage('bot', `Error: ${data.error}`);
            return;
        }

        displayMessage('bot', data.text_response);
        updateMoodDisplay(data.mood);

        const audio = new Audio(data.audio_url);
        audio.play();
    } catch (error) {
        displayMessage('bot', 'An error occurred. Please try again.');
        console.error('Error:', error);
    } finally {
        spinner.style.display = 'none';
        sendButton.disabled = false;
        messageInput.disabled = false;
    }
}

sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

window.onload = () => {
    displayMessage('bot', "Hello, I'm here to listen. What's on your mind?");
};