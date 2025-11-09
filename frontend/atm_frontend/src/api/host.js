import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  // Try to get token from localStorage (stored as JSON object by AuthContext)
  try {
    const tokensData = localStorage.getItem('tokens');
    if (tokensData) {
      const tokens = JSON.parse(tokensData);
      if (tokens.access) {
        config.headers.Authorization = `Bearer ${tokens.access}`;
      }
    }
  } catch (error) {
    console.error('Error retrieving token from localStorage:', error);
  }
  return config;
});

// Host API functions
export const hostAPI = {
  // Get all technicians
  getTechnicians: async () => {
    try {
      console.log('[API] Calling GET /host/technicians/');
      const response = await api.get('/host/technicians/');
      console.log('[API] Response status:', response.status);
      console.log('[API] Response data:', response.data);
      return response.data;
    } catch (error) {
      console.error('[API] Error in getTechnicians:', error);
      console.error('[API] Error name:', error.name);
      console.error('[API] Error message:', error.message);
      console.error('[API] Error response:', error.response);
      throw error.response?.data || error.message;
    }
  },

  // Create technician
  createTechnician: async (data) => {
    try {
      const response = await api.post('/host/technicians/', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Upload Excel file
  uploadExcel: async (formData) => {
    try {
      const response = await api.post('/host/upload-excel', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get uploaded device types for a technician
  getUploadedTypes: async (technicianId) => {
    const url = `/host/technicians/${technicianId}/uploaded-types`;
    try {
      console.log(`[API] Calling GET ${url}`);
      const response = await api.get(url);
      console.log(`[API] Response status: ${response.status}`);
      console.log(`[API] Response data:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`[API] Error calling GET ${url}:`, error);
      throw error.response?.data || error.message;
    }
  },

  // Get detailed uploaded files for a technician
  getUploadedFiles: async (technicianId) => {
    const url = `/host/technicians/${technicianId}/uploaded-files`;
    try {
      console.log(`[API] Calling GET ${url}`);
      const response = await api.get(url);
      console.log(`[API] Response status: ${response.status}`);
      console.log(`[API] Response data:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`[API] Error calling GET ${url}:`, error);
      throw error.response?.data || error.message;
    }
  },

  // Get dashboard statistics
  getDashboardStats: async () => {
    try {
      const response = await api.get('/host/dashboard-stats');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Delete technician and all related data
  deleteTechnician: async (technicianId) => {
    try {
      const response = await api.delete(`/host/technicians/${technicianId}/`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export default api;
