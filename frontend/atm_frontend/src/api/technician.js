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

// Technician API functions
export const technicianAPI = {
  // Get Excel data for logged-in technician
  getMyExcelData: async () => {
    try {
      const response = await api.get('/technician/my-excel-data');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get Excel data for specific device type
  getExcelDataByType: async (deviceType) => {
    try {
      // Encode device type to handle spaces and special characters
      const encodedType = encodeURIComponent(deviceType);
      const url = `/technician/excel-data/${encodedType}`;
      console.log(`[API] Calling GET ${url} (original: ${deviceType})`);
      const response = await api.get(url);
      console.log(`[API] Response status: ${response.status}`);
      console.log(`[API] Response data:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`[API] Error calling GET /technician/excel-data/${deviceType}:`, error);
      throw error.response?.data || error.message;
    }
  },

  // Get devices assigned to technician with optional filters
  getDevices: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      
      if (filters.type && filters.type !== 'All') {
        params.append('type', filters.type);
      }
      
      if (filters.status) {
        params.append('status', filters.status);
      }
      
      const queryString = params.toString();
      const url = `/technician/devices${queryString ? `?${queryString}` : ''}`;
      
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Submit maintenance with photos
  submitMaintenance: async (formData) => {
    try {
      const response = await api.post('/technician/submit', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export default api;
