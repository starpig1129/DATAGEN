// Initialize all components and handle state updates
document.addEventListener('DOMContentLoaded', () => {
    // Initial renders
    state.render();
    fileManager.render();

    // Set up state change handler
    setInterval(() => {
        // Update chat messages from state
        if (state.data.messages) {
            chatManager.updateFromState(state.data.messages);
        }
    }, 1000);

    // Disable input while processing
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.querySelector('.chat-input button');

    function updateInputState(disabled) {
        messageInput.disabled = disabled;
        sendButton.disabled = disabled;
        sendButton.style.opacity = disabled ? '0.5' : '1';
    }

    // Watch for processing state changes
    setInterval(() => {
        updateInputState(chatManager.isProcessing);
    }, 100);

    // Add loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.style.display = 'none';
    loadingIndicator.textContent = 'Processing...';
    document.querySelector('.chat-input').appendChild(loadingIndicator);

    // Update loading indicator based on processing state
    setInterval(() => {
        loadingIndicator.style.display = chatManager.isProcessing ? 'block' : 'none';
    }, 100);
});

// Add error handling for fetch requests
window.addEventListener('unhandledrejection', event => {
    console.error('Unhandled promise rejection:', event.reason);
    // You might want to show this in the UI
    const errorMessage = 'Error connecting to server. Please check if the server is running.';
    chatManager.addMessage(errorMessage);
});
