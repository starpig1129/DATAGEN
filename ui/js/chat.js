class ChatManager {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.chatMessages = document.getElementById('chatMessages');
        this.sendButton = document.getElementById('sendButton');
        this.isProcessing = false;
        
        // Bind event listeners
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isProcessing) {
                this.sendMessage();
            }
        });

        // Bind the send button click event
        this.sendButton.addEventListener('click', () => this.sendMessage());

        // Expose instance globally for state updates
        window.chatManager = this;
    }

    clearMessages() {
        this.chatMessages.innerHTML = '';
    }

    addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
        messageDiv.textContent = message;
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    addDecisionButtons() {
        const buttonsDiv = document.createElement('div');
        buttonsDiv.className = 'decision-buttons';
        
        const option1 = document.createElement('button');
        option1.textContent = 'Regenerate hypothesis';
        option1.onclick = () => this.sendMessage('', '1');
        
        const option2 = document.createElement('button');
        option2.textContent = 'Continue research';
        option2.onclick = () => this.sendMessage('', '2');
        
        buttonsDiv.appendChild(option1);
        buttonsDiv.appendChild(option2);
        this.chatMessages.appendChild(buttonsDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    async sendMessage(customMessage = '', processDecision = '') {
        const message = customMessage || this.messageInput.value.trim();
        
        if ((message || processDecision) && !this.isProcessing) {
            this.isProcessing = true;
            this.messageInput.disabled = true;
            this.sendButton.disabled = true;
            
            if (message) {
                this.addMessage(message, true);
                this.messageInput.value = '';
            }

            // Add loading indicator
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message system-message';
            loadingDiv.textContent = 'Processing...';
            this.chatMessages.appendChild(loadingDiv);
            
            try {
                console.log('Sending request:', { message, process_decision: processDecision });
                
                // Send message to backend using dynamic base URL
                const response = await fetch(`${window.apiConfig.apiBaseUrl}/api/send_message`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        message,
                        process_decision: processDecision
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                console.log('Received response:', result);
                
                // Remove loading indicator
                this.chatMessages.removeChild(loadingDiv);
                
                if (result.status === 'success') {
                    // Update state if provided in response
                    if (result.state && window.state) {
                        window.state.update(result.state);
                    }
                    
                    // Check if we need to show decision buttons
                    if (result.needs_decision) {
                        this.addMessage('Please choose the next step:');
                        this.addDecisionButtons();
                    }
                } else {
                    console.error('Error:', result.message);
                    this.addMessage('Error: ' + result.message);
                }
            } catch (error) {
                console.error('Error sending message:', error);
                // Remove loading indicator
                this.chatMessages.removeChild(loadingDiv);
                this.addMessage('Error: Failed to send message. Please try again.');
            } finally {
                this.isProcessing = false;
                this.messageInput.disabled = false;
                this.sendButton.disabled = false;
                this.messageInput.focus();
            }
        }
    }

    // Update messages from state
    updateFromState(messages) {
        if (!messages) return;
        
        // Clear existing messages
        this.clearMessages();
        
        // Add all messages from state
        messages.forEach(message => {
            if (message && message.content) {
                this.addMessage(message.content, message.type === 'human');
            }
        });
    }
}

// Create global chat instance
const chatManager = new ChatManager();
