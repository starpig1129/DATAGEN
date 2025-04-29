'use strict';

import {config} from './config.js';

/**
 * @fileoverview Manages the application state and updates the UI accordingly.
 */

/**
 * Represents the application state and handles fetching and rendering.
 */
class State {
  /**
   * Initializes the State instance.
   */
  constructor() {
    /**
     * The application state data.
     * @type {{
     *   messages: Array<Object>,
     *   hypothesis: string,
     *   process: string,
     *   process_decision: string,
     *   visualization_state: string,
     *   searcher_state: string,
     *   code_state: string,
     *   report_section: string,
     *   quality_review: string,
     *   needs_revision: boolean,
     *   sender: string,
     *   needs_decision: boolean
     * }}
     * @private
     */
    this.data_ = {
      messages: [],
      hypothesis: '',
      process: '',
      process_decision: '',
      visualization_state: '',
      searcher_state: '',
      code_state: '',
      report_section: '',
      quality_review: '',
      needs_revision: false,
      sender: '',
      needs_decision: false, // Added needs_decision to initial state
    };

    /**
     * The DOM element to display the state content.
     * @private {?HTMLElement}
     */
    this.stateContentElement_ = document.getElementById('stateContent');

    // Initial fetch of state and SSE connection are handled in main.js
  }

  /**
   * Fetches the current state from the backend API.
   * @async
   */
  async fetchState() {
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/state`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const newState = await response.json();
      this.update(newState);
    } catch (error) {
      console.error('Error fetching state:', error);
      // Optionally, display an error message in the UI
    }
  }

  /**
   * Updates the internal state data and triggers a re-render.
   * @param {!Object} newState The new state object received from the backend.
   */
  update(newState) {
    // Basic check to see if the core data structure is different
    // A more sophisticated diffing could be implemented if needed
    if (JSON.stringify(this.data_) !== JSON.stringify(newState)) {
        this.data_ = newState; // Directly assign the new state object
        this.render();
        // Dispatch a custom event to notify other components about the state change
        document.dispatchEvent(new CustomEvent('stateUpdated', { detail: this.data_ }));
    }
  }

  /**
   * Renders the current state data to the UI.
   * Uses more granular DOM updates instead of innerHTML overwrite.
   */
  render() {
    if (!this.stateContentElement_) {
      console.error('State content element not found.');
      return;
    }

    // Clear previous content efficiently
    while (this.stateContentElement_.firstChild) {
      this.stateContentElement_.removeChild(this.stateContentElement_.firstChild);
    }

    // Render Active Agent first if available
    if (this.data_.sender) {
      this.stateContentElement_.appendChild(
          this.createStateItemElement_('ACTIVE AGENT', this.data_.sender, true));
    }

    // Render other state items
    Object.entries(this.data_).forEach(([key, value]) => {
      // Skip messages (handled by ChatManager) and sender (already handled)
      if (key !== 'messages' && key !== 'sender') {
        const label = key.replace(/_/g, ' ').toUpperCase();
        this.stateContentElement_.appendChild(
            this.createStateItemElement_(label, value || 'Not set'));
      }
    });
  }

  /**
   * Creates a DOM element for a single state item.
   * @param {string} labelText The label text for the state item.
   * @param {string|boolean|number} valueText The value text for the state item.
   * @param {boolean} [isActiveAgent=false] Whether this item represents the active agent.
   * @return {!HTMLElement} The created state item element.
   * @private
   */
  createStateItemElement_(labelText, valueText, isActiveAgent = false) {
    const itemElement = document.createElement('div');
    itemElement.className = 'state-item';
    if (isActiveAgent) {
      itemElement.classList.add('active-agent');
    }

    const labelElement = document.createElement('div');
    labelElement.className = 'state-label';
    labelElement.textContent = labelText;

    const valueElement = document.createElement('div');
    valueElement.className = 'state-value';
    // Handle boolean values explicitly
    valueElement.textContent = typeof valueText === 'boolean' ? String(valueText) : valueText;

    itemElement.appendChild(labelElement);
    itemElement.appendChild(valueElement);
    return itemElement;
  }

  /**
   * Gets the current state data.
   * @return {!Object} The current state data.
   */
  getData() {
    return this.data_;
  }
  /**
   * Connects to the backend SSE stream for real-time state updates.
   */
  connectToSSEStream() {
    const eventSourceUrl = `${config.apiBaseUrl}/stream`;
    console.log(`Connecting to SSE stream at ${eventSourceUrl}`);
    const eventSource = new EventSource(eventSourceUrl);

    eventSource.addEventListener('state_update', (event) => {
      try {
        const newState = JSON.parse(event.data);
        console.log('Received state update via SSE:', newState);
        this.update(newState);
      } catch (error) {
        console.error('Error parsing SSE data:', error, 'Raw data:', event.data);
      }
    });

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      // Optionally implement reconnection logic here
      eventSource.close(); // Close the connection on error
      // Consider adding a delay before attempting to reconnect
      // setTimeout(() => this.connectToSSEStream(), 5000); // Example reconnect
    };

    // Optional: Handle the initial open event
    eventSource.onopen = () => {
      console.log('SSE connection opened successfully.');
    };
  }
}

// Create and export the singleton state instance
const state = new State();

export {State, state};
