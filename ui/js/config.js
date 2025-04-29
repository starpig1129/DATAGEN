'use strict';

/**
 * @fileoverview Configuration for the API endpoint.
 */

/**
 * API Configuration object.
 * @const
 */
const config = {
  /**
   * The base URL for API requests.
   * Dynamically determined from the current window location.
   * @type {string}
   */
  apiBaseUrl: `${window.location.protocol}//${window.location.host}`,
};

// Export the configuration object for use in other modules.
export {config};
