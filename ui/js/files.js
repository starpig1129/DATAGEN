'use strict';

import {config} from './config.js';

/**
 * @fileoverview Manages fetching and displaying the list of data storage files.
 */

/**
 * Handles fetching and rendering the list of files from the data storage.
 */
class FileManager {
  /**
   * Initializes the FileManager instance.
   */
  constructor() {
    /**
     * Array storing the list of file names.
     * @type {!Array<string>}
     * @private
     */
    this.files_ = [];

    /**
     * The DOM element where the file list is rendered.
     * @private {?HTMLElement}
     */
    this.filesContentElement_ = document.getElementById('filesContent');

    /**
     * Interval ID for file list polling.
     * @private {?number}
     */
    this.pollingIntervalId_ = null;

    if (!this.filesContentElement_) {
      console.error('Files content element not found.');
    }
  }

  /**
   * Fetches the list of files from the backend API.
   * @async
   */
  async fetchFiles() {
    try {
      const response = await fetch(`${config.apiBaseUrl}/api/files`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      // Only update and render if the file list has actually changed
      if (JSON.stringify(this.files_) !== JSON.stringify(data.files)) {
        this.updateFiles(data.files || []); // Ensure it's always an array
      }
    } catch (error) {
      console.error('Error fetching files:', error);
      // Optionally display an error in the UI
    }
  }

  /**
   * Starts polling the backend for file list updates.
   * TODO: Replace polling with a more efficient mechanism like WebSockets or SSE
   *       once backend support is available. This is a known performance bottleneck.
   */
  startPolling() {
    if (this.pollingIntervalId_) {
      clearInterval(this.pollingIntervalId_); // Clear existing interval
    }
    // Poll every 5 seconds
    this.pollingIntervalId_ = setInterval(() => this.fetchFiles(), 5000);
    console.log('File list polling started (Interval: 5000ms). Note: This will be replaced.');
  }

   /**
   * Stops polling for file list updates.
   */
  stopPolling() {
    if (this.pollingIntervalId_) {
      clearInterval(this.pollingIntervalId_);
      this.pollingIntervalId_ = null;
      console.log('File list polling stopped.');
    }
  }


  /**
   * Updates the internal file list and triggers a re-render.
   * @param {!Array<string>} newFiles The new list of file names.
   * @private
   */
  updateFiles(newFiles) {
    this.files_ = newFiles;
    this.render();
  }

  /**
   * Renders the list of files to the UI.
   * Uses more granular DOM updates instead of innerHTML overwrite.
   */
  render() {
    if (!this.filesContentElement_) {
      return; // Element not found, cannot render
    }

    // Clear previous content efficiently
    while (this.filesContentElement_.firstChild) {
      this.filesContentElement_.removeChild(this.filesContentElement_.firstChild);
    }

    // Render new file items
    if (this.files_.length === 0) {
        const noFilesItem = document.createElement('div');
        noFilesItem.className = 'file-item file-item--empty'; // Add a specific class for styling
        noFilesItem.textContent = 'No files found.';
        this.filesContentElement_.appendChild(noFilesItem);
    } else {
        this.files_.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.textContent = file;
            // TODO: Add click handler to view file content if needed in the future
            this.filesContentElement_.appendChild(fileItem);
        });
    }
  }
}

// Create and export the singleton file manager instance
const fileManager = new FileManager();

export {FileManager, fileManager};
