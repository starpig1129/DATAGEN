'use strict';

import {config} from './config.js';

/**
 * @fileoverview Manages the chat interface, including sending messages,
 * displaying messages, and handling user decisions.
 */

/**
 * Handles chat UI interactions and communication with the backend.
 */
class ChatManager {
  /**
   * Initializes the ChatManager instance and sets up event listeners.
   */
  constructor() {
    /** @private {?HTMLInputElement} */
    this.messageInputElement_ = document.getElementById('messageInput');
    /** @private {?HTMLElement} */
    this.chatMessagesElement_ = document.getElementById('chatMessages');
    /** @private {?HTMLButtonElement} */
    this.sendButtonElement_ = document.getElementById('sendButton');
    /** @private {?HTMLElement} */
    this.decisionButtonsContainer_ = document.getElementById('decision-buttons');
    /** @private {?HTMLButtonElement} */
    this.regenerateButtonElement_ = document.getElementById('regenerate-button');
    /** @private {?HTMLButtonElement} */
    this.continueButtonElement_ = document.getElementById('continue-button');

    /**
     * Flag indicating if a message request is currently being processed.
     * @type {boolean}
     */
    this.isProcessing = false; // Public property to be observed by main.js

    if (!this.messageInputElement_ || !this.chatMessagesElement_ ||
        !this.sendButtonElement_ || !this.decisionButtonsContainer_ ||
        !this.regenerateButtonElement_ || !this.continueButtonElement_) {
      console.error('One or more chat UI elements could not be found.');
      // Potentially disable functionality or show an error to the user
      return;
    }

    // Bind event listeners
    this.messageInputElement_.addEventListener('keypress', (e) => {
      // Send message on Enter key press, only if not processing
      if (e.key === 'Enter' && !this.isProcessing) {
        this.sendMessage();
      }
    });

    this.sendButtonElement_.addEventListener('click', () => this.sendMessage());

    // Bind decision button clicks
    this.regenerateButtonElement_.addEventListener('click', () => this.sendDecision_('1'));
    this.continueButtonElement_.addEventListener('click', () => this.sendDecision_('2'));
  }

  /**
   * Clears all messages from the chat display.
   */
  clearMessages() {
    if (!this.chatMessagesElement_) return;
    // Clear previous content efficiently
    while (this.chatMessagesElement_.firstChild) {
      this.chatMessagesElement_.removeChild(this.chatMessagesElement_.firstChild);
    }
  }

 /**
  * Adds a message to the chat display.
  * @param {string} message The message content (can be Markdown).
  * @param {boolean} [isUser=false] True if the message is from the user.
  * @param {string} [sender=''] The sender's name (for non-user messages).
  */
  addMessage(message, isUser = false, sender = '') {
    if (!this.chatMessagesElement_) return;

    const messageDiv = document.createElement('div');
    // Using BEM style modifiers for clarity
    messageDiv.className = `message ${isUser ? 'message--user' : 'message--assistant'}`;

    // Parse Markdown to HTML using marked, then sanitize with DOMPurify.
    let sanitizedHtml = '';
    if (typeof marked !== 'undefined') {
      const rawHtml = marked.parse(message); // Parse Markdown without marked's sanitizer
      if (typeof DOMPurify !== 'undefined') {
        sanitizedHtml = DOMPurify.sanitize(rawHtml); // Sanitize with DOMPurify
      } else {
        console.warn('DOMPurify library not loaded. Using marked\'s built-in sanitizer as fallback.');
        // Fallback to marked's sanitizer if DOMPurify is missing
        sanitizedHtml = marked.parse(message, { sanitize: true });
      }
    } else {
      console.error('Marked library is not loaded. Rendering message as plain text.');
      // Fallback to plain text if marked is missing
      const textNode = document.createTextNode(message);
      messageDiv.appendChild(textNode); // Append text node directly
      sanitizedHtml = null; // Indicate that innerHTML should not be set
    }

    if (sanitizedHtml !== null) {
        messageDiv.innerHTML = sanitizedHtml;
    }

    // Add sender information using data attribute for styling/identification
    messageDiv.setAttribute('data-sender', isUser ? 'User' : (sender || 'Assistant'));

    this.chatMessagesElement_.appendChild(messageDiv);
    // Automatically scroll to the bottom when a new message is added
    this.chatMessagesElement_.scrollTop = this.chatMessagesElement_.scrollHeight;
  }


  /**
   * Updates the chat display based on the messages array from the state.
   * This method compares the new messages with the currently displayed ones
   * and adds only the new messages to avoid full re-renders.
   * @param {!Array<Object>} newMessages The array of message objects from the state.
   */
   updateFromState(newMessages) {
    if (!newMessages || !this.chatMessagesElement_) return;

    const currentMessagesCount = this.chatMessagesElement_.children.length;
    const newMessagesCount = newMessages.length;

    // Only add messages that are new
    if (newMessagesCount > currentMessagesCount) {
      for (let i = currentMessagesCount; i < newMessagesCount; i++) {
        const message = newMessages[i];
        if (message && message.content) {
          this.addMessage(
              message.content,
              message.type === 'human', // Assuming 'human' type for user messages
              message.sender || (message.type === 'human' ? 'User' : 'Assistant')
          );
        }
      }
      // Scrolling is handled within addMessage now.
    } else if (newMessagesCount < currentMessagesCount) {
      // If messages were somehow removed from the state (less likely scenario)
      // A full re-render is safer to ensure consistency.
      console.warn('Message count decreased in state. Performing full re-render of chat.');
      this.clearMessages();
      newMessages.forEach(message => {
        if (message && message.content) {
          this.addMessage(
              message.content,
              message.type === 'human',
              message.sender || (message.type === 'human' ? 'User' : 'Assistant')
          );
        }
      });
      // Scrolling handled by the last addMessage call.
    }
    // If counts are the same, assume no change needed for chat display.
  }


  /**
   * Shows or hides the decision buttons based on the backend state.
   * Also enables/disables the message input and send button accordingly.
   * @param {boolean} needsDecision Whether the user needs to make a decision.
   */
  handleDecisionNeeded(needsDecision) {
    if (!this.decisionButtonsContainer_ || !this.messageInputElement_ || !this.sendButtonElement_) return;

    if (needsDecision) {
      this.decisionButtonsContainer_.style.display = 'flex'; // Use flex for proper layout
      this.updateInputDisabledState_(true); // Disable text input and send button
    } else {
      this.decisionButtonsContainer_.style.display = 'none';
      // Re-enable input only if not currently processing another request
      if (!this.isProcessing) {
          this.updateInputDisabledState_(false);
      }
    }
  }

  /**
   * Sends the user's decision to the backend.
   * @param {string} decision The decision code ('1' for regenerate, '2' for continue).
   * @private
   */
  async sendDecision_(decision) {
    // Immediately hide buttons. Input remains disabled until sendMessage completes.
    this.handleDecisionNeeded(false);
    // Call sendMessage with an empty message and the decision code.
    await this.sendMessage('', decision);
  }

  /**
   * Sends a message or a decision to the backend API.
   * Manages the processing state and disables/enables input fields.
   * @param {string} [customMessage=''] The message text from the input field or elsewhere.
   * @param {string} [processDecision=''] The decision code ('1' or '2') if sending a decision.
   * @async
   */
  async sendMessage(customMessage = '', processDecision = '') {
console.log('sendMessage called with:', { customMessage, processDecision });
    // Ensure elements are available before proceeding
    if (!this.messageInputElement_ || !this.sendButtonElement_) return;

    const message = customMessage || this.messageInputElement_.value.trim();

console.log('Checking condition:', { message, processDecision, isProcessing: this.isProcessing });
    // Proceed only if there's a message OR a decision, and not already processing.
    if ((message || processDecision) && !this.isProcessing) {
      this.isProcessing = true;
      this.updateInputDisabledState_(true); // Disable input/button
console.log('Condition met, setting isProcessing=true');

      // Add user message to chat immediately if it exists
      if (message) {
        this.addMessage(message, true); // Sender is implicitly 'User'
        this.messageInputElement_.value = ''; // Clear input field after sending
      }

      // Notify main.js that processing has started (for loading indicator)
      document.dispatchEvent(new CustomEvent('processingStateChanged', { detail: { isProcessing: true } }));


      try {
        console.log('Sending request:', { message, process_decision: processDecision });

console.log('About to fetch /api/send_message');
        // Send message/decision to the backend
        const response = await fetch(`${config.apiBaseUrl}/api/send_message`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message,
            process_decision: processDecision
          })
        });

        // Handle HTTP errors
        if (!response.ok) {
          let errorDetails = `HTTP error! status: ${response.status}`;
          try {
              // Attempt to parse error message from response body
              const errorData = await response.json();
              errorDetails += ` - ${errorData.message || 'No details provided.'}`;
          } catch (e) {
              // Ignore if response body is not JSON or empty
              console.warn('Could not parse error response body.');
          }
          throw new Error(errorDetails);
        }

        // Process successful response
            // Process successful response
            const result = await response.json();
            console.log('Received immediate response:', result); // Modified log

            if (result.status === 'processing') {
              // Backend acknowledged the request and is processing it in the background.
              console.log('Backend is processing the message.');
              // No further action needed here, wait for SSE update.
            } else if (result.status !== 'processing') { // Handle unexpected statuses from the immediate response
              console.error('Unexpected API Status:', result.status, result.message);
              this.addMessage(`錯誤: 後端返回意外狀態 (${result.status})`, false, 'System');
            }
      } catch (error) {
        // Handle network errors or issues during fetch/parsing
        console.error('Error sending message:', error);
        this.addMessage(`錯誤: 發送消息失敗 (${error.message})`, false, 'System');
      } finally {
console.log('sendMessage finally block reached');
        this.isProcessing = false;
        // Re-enable input/button ONLY if no decision is currently needed
        if (!this.decisionButtonsContainer_.style.display || this.decisionButtonsContainer_.style.display === 'none') {
            this.updateInputDisabledState_(false);
        }
        // Always refocus the input field for better UX
        this.messageInputElement_.focus();

        // Notify main.js that processing has ended
         document.dispatchEvent(new CustomEvent('processingStateChanged', { detail: { isProcessing: false } }));
      }
    } else if (this.isProcessing) {
        console.warn('sendMessage called while already processing.');
    }
  }

  /**
   * Updates the disabled state of the message input and send button.
   * @param {boolean} isDisabled Whether the elements should be disabled.
   * @private
   */
  updateInputDisabledState_(isDisabled) {
    if (this.messageInputElement_ && this.sendButtonElement_) {
      this.messageInputElement_.disabled = isDisabled;
      this.sendButtonElement_.disabled = isDisabled;
      // Optionally add visual cues like opacity
      // this.sendButtonElement_.style.opacity = isDisabled ? '0.5' : '1';
    }
  }
}

// Export the ChatManager class
export { ChatManager };
