const API_KEY = 'AIzaSyDGaETHQxRDchK9icNKOKwCFynWpMmqTDA';
const API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent';

const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');

let isProcessing = false;

async function sendMessage() {
    if (isProcessing || !userInput.value.trim()) return;

    const userMessage = userInput.value.trim();
    addMessage(userMessage, 'user');
    userInput.value = '';
    isProcessing = true;
    sendButton.disabled = true;

    try {
        const response = await fetch(`${API_URL}?key=${API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: userMessage
                    }]
                }]
            })
        });

        const data = await response.json();
        
        if (data.candidates && data.candidates[0].content) {
            const aiResponse = data.candidates[0].content.parts[0].text;
            addMessage(aiResponse, 'ai');
        } else {
            throw new Error('No valid response from AI');
        }
    } catch (error) {
        console.error('Error:', error);
        addMessage('عذراً، حدث خطأ في معالجة طلبك. يرجى المحاولة مرة أخرى.', 'ai');
    } finally {
        isProcessing = false;
        sendButton.disabled = false;
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

sendButton.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Enable textarea auto-resize
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
    if (this.scrollHeight > 150) {
        this.style.height = '150px';
    }
});
