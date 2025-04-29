'use strict';

import { state } from './state.js';
import { fileManager } from './files.js';
import { ChatManager } from './chat.js';

/**
 * @fileoverview Main entry point for the UI application.
 * Initializes modules, sets up event listeners, and handles global concerns.
 */

/**
 * Reference to the loading indicator element.
 * @private {?HTMLElement}
 */
let loadingIndicatorElement_ = null;

/**
 * Reference to the ChatManager instance. Initialized in initApp.
 * @private {?ChatManager}
 */
let chatManager = null;

/**
 * Creates and appends the loading indicator element to the chat input area.
 * @private
 */
function setupLoadingIndicator_() {
  const chatInputElement = document.querySelector('.chat__input'); // Corrected selector
  if (!chatInputElement) {
    console.error('Chat input container not found for loading indicator.');
    return;
  }

  loadingIndicatorElement_ = document.createElement('div');
  loadingIndicatorElement_.className = 'loading-indicator'; // Use class for styling
  loadingIndicatorElement_.textContent = 'Processing...';
  loadingIndicatorElement_.style.display = 'none'; // Initially hidden
  // Prepend inside chat-input for better positioning control via CSS
  chatInputElement.prepend(loadingIndicatorElement_);
}

/**
 * Shows or hides the loading indicator.
 * @param {boolean} show True to show, false to hide.
 * @private
 */
function toggleLoadingIndicator_(show) {
  if (loadingIndicatorElement_) {
    loadingIndicatorElement_.style.display = show ? 'block' : 'none';
  }
}

/**
 * Handles updates received from the state module.
 * @param {CustomEvent} event The 'stateUpdated' event object.
 * @private
 */
function handleStateUpdate_(event) {
  const newState = event.detail;
  if (!newState) return;

  // Update chat messages based on the new state
  if (newState.messages) {
    chatManager.updateFromState(newState.messages);
  }

  // Update decision buttons visibility based on the new state
  chatManager.handleDecisionNeeded(newState.needs_decision || false);

  // Note: State rendering is handled within state.js's render method.
  // Note: File list rendering is handled within fileManager.js's render method.
}

/**
 * Handles changes in the processing state from the chat module.
 * @param {CustomEvent} event The 'processingStateChanged' event object.
 * @private
 */
function handleProcessingStateChange_(event) {
    const isProcessing = event.detail.isProcessing;
    toggleLoadingIndicator_(isProcessing);
    // Input disabling/enabling is handled within chatManager.js
}


/**
 * Sets up a global error handler for unhandled promise rejections.
 * @private
 */
function setupGlobalErrorHandler_() {
  window.addEventListener('unhandledrejection', event => {
    console.error('Unhandled promise rejection:', event.reason);
    // Display a user-friendly error message in the chat
    const errorMessage = `發生未預期的錯誤： ${event.reason.message || event.reason || '無法連接伺服器，請檢查後端是否運行。'}`;
    // Ensure chatManager is available before trying to add a message
    if (chatManager) {
        chatManager.addMessage(errorMessage, false, 'System Error');
    } else {
        alert(errorMessage); // Fallback if chat is not ready
    }
    // Potentially hide loading indicator if an error occurs during processing
    toggleLoadingIndicator_(false);
    // Re-enable input if chatManager is available
    if (chatManager && chatManager.updateInputDisabledState_) {
        chatManager.updateInputDisabledState_(false);
    }
  });
}

/**
 * Initializes the application components and starts data fetching/SSE connection.
 */
async function initApp() { // Make initApp async
  console.log('Initializing application...');

  // Ensure DOM elements required by managers are present before proceeding
  if (!document.getElementById('chatMessages') ||
      !document.getElementById('stateContent') ||
      !document.getElementById('filesContent')) {
     console.error('Core UI elements missing. Aborting initialization.');
     alert('UI 初始化失敗，缺少必要的頁面元素。');
     return;
  }
// Initialize ChatManager now that core elements are confirmed
  chatManager = new ChatManager();

  // Setup UI elements like the loading indicator
  setupLoadingIndicator_();

  // Setup event listeners for inter-module communication
  document.addEventListener('stateUpdated', handleStateUpdate_);
  document.addEventListener('processingStateChanged', handleProcessingStateChange_);

  // Setup global error handling
  setupGlobalErrorHandler_();

  // Perform initial data fetches
  // Rendering will be triggered by the 'stateUpdated' event or within fetch methods
  try {
    await state.fetchState(); // Wait for initial state fetch
    console.log('Initial state fetched successfully.');
    // Connect to SSE stream AFTER initial state is loaded
    state.connectToSSEStream();
  } catch (error) {
    console.error('Failed to fetch initial state:', error);
    // Handle error appropriately, maybe show a message to the user
    chatManager.addMessage('無法載入初始應用程式狀態，請稍後再試。', false, 'System Error');
  }

  fileManager.fetchFiles(); // Fetch initial file list

  // Start file polling (state polling is replaced by SSE)
  // state.startPolling(); // Removed state polling
  fileManager.startPolling(); // Keep file polling for now

  console.log('Application initialized.');
}

// Wait for the DOM to be fully loaded before initializing the application
document.addEventListener('DOMContentLoaded', initApp);
