import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Authentication API functions
export const authAPI = {
  // Login user
  login: async (username, password) => {
    try {
      const response = await api.post(
        '/auth/login/',
        { username, password }
      );

      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Refresh token
  refreshToken: async (refreshToken) => {
    try {
      const response = await api.post(
        '/auth/refresh/',
        { refresh: refreshToken }
      );
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
};

export default api;