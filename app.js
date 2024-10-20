document.getElementById('send-btn').addEventListener('click', function() {
    let userInput = document.getElementById('user-input').value;
    if (userInput.trim() === "") return;

    // Display user message
    let chatBox = document.getElementById('chat-box');
    let userMessage = document.createElement('div');
    userMessage.className = 'chat-message user-message';
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Clear input field
    document.getElementById('user-input').value = "";

    // Send user input to the backend
    fetch('/send_message', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `message=${encodeURIComponent(message)}`,
    })
    .then(response => response.json())
    .then(data => {
        displayMessage(data.response, 'bot');
    });
    
});
