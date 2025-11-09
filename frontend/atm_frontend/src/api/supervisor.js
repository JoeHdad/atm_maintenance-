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

// Supervisor API functions
export const supervisorAPI = {
  // Get all submissions with filters
  getSubmissions: async (filters = {}) => {
    try {
      const params = new URLSearchParams();
      
      if (filters.status && filters.status !== 'All') {
        params.append('status', filters.status);
      }
      
      if (filters.device_type && filters.device_type !== 'All') {
        params.append('device_type', filters.device_type);
      }
      
      if (filters.technician_id) {
        params.append('technician_id', filters.technician_id);
      }
      
      if (filters.date_from) {
        params.append('date_from', filters.date_from);
      }
      
      if (filters.date_to) {
        params.append('date_to', filters.date_to);
      }
      
      const queryString = params.toString();
      const url = `/supervisor/submissions${queryString ? `?${queryString}` : ''}`;
      
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get submission detail
  getSubmissionDetail: async (id) => {
    try {
      const response = await api.get(`/supervisor/submissions/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Approve submission
  approveSubmission: async (id, remarks = '') => {
    try {
      const response = await api.patch(`/supervisor/submissions/${id}/approve`, {
        remarks
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Reject submission
  rejectSubmission: async (id, remarks) => {
    try {
      const response = await api.patch(`/supervisor/submissions/${id}/reject`, {
        remarks
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get dashboard statistics
  getDashboardStats: async () => {
    try {
      const response = await api.get('/supervisor/dashboard-stats');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Preview PDF before approval
  previewPDF: async (id) => {
    try {
      const response = await api.post(`/supervisor/submissions/${id}/preview-pdf`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

// Export individual functions for convenience
export const getSubmissions = supervisorAPI.getSubmissions;
export const getSubmissionDetail = supervisorAPI.getSubmissionDetail;
export const approveSubmission = supervisorAPI.approveSubmission;
export const rejectSubmission = supervisorAPI.rejectSubmission;
export const getDashboardStats = supervisorAPI.getDashboardStats;

export default api;
