import axios from 'axios';

// Base URL for API requests
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// API service functions
const apiService = {
  // User registration
  registerUser: async (userData) => {
    try {
      const response = await api.post('/users/register', userData);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Get Sumsub access token
  getSumsubToken: async (userId) => {
    try {
      const response = await api.get(`/verification/token/${userId}`);
      return response.data.token;
    } catch (error) {
      throw handleApiError(error);
    }
  },
  
  // Get verification status
  getVerificationStatus: async (userId) => {
    try {
      const response = await api.get(`/verification/status/${userId}`);
      return response.data.status;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// Helper function to handle API errors
const handleApiError = (error) => {
  if (error.response) {
    // The request was made and the server responded with a status code
    // that falls out of the range of 2xx
    const errorMessage = error.response.data.message || 'An error occurred';
    return new Error(errorMessage);
  } else if (error.request) {
    // The request was made but no response was received
    return new Error('No response from server. Please check your internet connection.');
  } else {
    // Something happened in setting up the request that triggered an Error
    return new Error('Error setting up request. Please try again.');
  }
};

export default apiService;
