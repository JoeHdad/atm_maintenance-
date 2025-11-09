/**
 * API Interceptors for Error Handling
 * Handles common API errors and provides user-friendly messages
 */

// Error message mapping
const ERROR_MESSAGES = {
  400: 'Invalid request. Please check your input.',
  401: 'Your session has expired. Please log in again.',
  403: 'You do not have permission to perform this action.',
  404: 'The requested resource was not found.',
  500: 'Server error. Please try again later.',
  503: 'Service temporarily unavailable. Please try again later.',
  NETWORK_ERROR: 'Network error. Please check your internet connection.',
  TIMEOUT: 'Request timeout. Please try again.',
  UNKNOWN: 'An unexpected error occurred. Please try again.'
};

/**
 * Setup axios interceptors for request and response
 * @param {Object} axiosInstance - Axios instance to add interceptors to
 * @param {Function} onUnauthorized - Callback for 401 errors (e.g., logout)
 * @param {Function} showToast - Toast notification function
 */
export const setupInterceptors = (axiosInstance, onUnauthorized, showToast) => {
  // Request interceptor
  axiosInstance.interceptors.request.use(
    (config) => {
      // Add auth token if available
      const tokens = localStorage.getItem('tokens');
      if (tokens) {
        try {
          const parsedTokens = JSON.parse(tokens);
          if (parsedTokens.access) {
            config.headers.Authorization = `Bearer ${parsedTokens.access}`;
          }
        } catch (error) {
          console.error('Error parsing tokens:', error);
        }
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor
  axiosInstance.interceptors.response.use(
    (response) => {
      // Success response
      return response;
    },
    async (error) => {
      const originalRequest = error.config;

      // Handle different error scenarios
      if (!error.response) {
        // Network error
        const message = ERROR_MESSAGES.NETWORK_ERROR;
        if (showToast) showToast(message, 'error');
        return Promise.reject({ message, type: 'network' });
      }

      const status = error.response.status;
      const data = error.response.data;

      // Handle 401 Unauthorized
      if (status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        // Try to refresh token
        const tokens = localStorage.getItem('tokens');
        if (tokens) {
          try {
            const parsedTokens = JSON.parse(tokens);
            const refreshResponse = await axiosInstance.post('/auth/token/refresh/', {
              refresh: parsedTokens.refresh
            });

            const newAccessToken = refreshResponse.data.access;
            const newTokens = { ...parsedTokens, access: newAccessToken };
            localStorage.setItem('tokens', JSON.stringify(newTokens));

            // Retry original request with new token
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
            return axiosInstance(originalRequest);
          } catch (refreshError) {
            // Refresh failed, logout user
            if (onUnauthorized) onUnauthorized();
            if (showToast) showToast(ERROR_MESSAGES[401], 'error');
            return Promise.reject({ message: ERROR_MESSAGES[401], type: 'auth' });
          }
        } else {
          // No refresh token, logout user
          if (onUnauthorized) onUnauthorized();
          if (showToast) showToast(ERROR_MESSAGES[401], 'error');
          return Promise.reject({ message: ERROR_MESSAGES[401], type: 'auth' });
        }
      }

      // Handle other status codes
      let message = ERROR_MESSAGES[status] || ERROR_MESSAGES.UNKNOWN;

      // Try to get more specific error message from response
      if (data) {
        if (typeof data === 'string') {
          message = data;
        } else if (data.detail) {
          message = data.detail;
        } else if (data.error) {
          message = data.error;
        } else if (data.message) {
          message = data.message;
        } else if (data.non_field_errors && Array.isArray(data.non_field_errors)) {
          message = data.non_field_errors[0];
        }
      }

      // Show toast notification
      if (showToast && status !== 401) {
        showToast(message, 'error');
      }

      // Return structured error
      return Promise.reject({
        message,
        status,
        data,
        type: 'api'
      });
    }
  );
};

/**
 * Handle validation errors from forms
 * @param {Object} error - Error object from API
 * @returns {Object} - Field-specific error messages
 */
export const handleValidationErrors = (error) => {
  const fieldErrors = {};

  if (error.data && typeof error.data === 'object') {
    Object.keys(error.data).forEach((field) => {
      const fieldError = error.data[field];
      if (Array.isArray(fieldError)) {
        fieldErrors[field] = fieldError[0];
      } else if (typeof fieldError === 'string') {
        fieldErrors[field] = fieldError;
      }
    });
  }

  return fieldErrors;
};

/**
 * Format error for display
 * @param {Object} error - Error object
 * @returns {String} - Formatted error message
 */
export const formatError = (error) => {
  if (typeof error === 'string') {
    return error;
  }

  if (error.message) {
    return error.message;
  }

  if (error.response && error.response.data) {
    const data = error.response.data;
    if (typeof data === 'string') return data;
    if (data.detail) return data.detail;
    if (data.error) return data.error;
    if (data.message) return data.message;
  }

  return ERROR_MESSAGES.UNKNOWN;
};

export default {
  setupInterceptors,
  handleValidationErrors,
  formatError,
  ERROR_MESSAGES
};
