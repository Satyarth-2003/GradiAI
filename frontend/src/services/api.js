import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configure axios defaults
axios.defaults.timeout = 120000; // 2 minutes for video analysis

export const apiService = {
  // Health check
  async healthCheck() {
    try {
      const response = await axios.get(`${API}/health`);
      return response.data;
    } catch (error) {
      throw new Error(`Health check failed: ${error.message}`);
    }
  },

  // Analyze YouTube video
  async analyzeVideo(youtubeUrl) {
    try {
      const response = await axios.post(`${API}/analyze-video`, {
        youtube_url: youtubeUrl
      });
      return response.data;
    } catch (error) {
      if (error.response) {
        // Server responded with error status
        const errorMessage = error.response.data?.detail || error.response.data?.error || 'Analysis failed';
        throw new Error(errorMessage);
      } else if (error.request) {
        // Request timeout or network error
        throw new Error('Network error - please check your connection and try again');
      } else {
        // Other error
        throw new Error(`Analysis error: ${error.message}`);
      }
    }
  },

  // Get recent analyses
  async getRecentAnalyses(limit = 10) {
    try {
      const response = await axios.get(`${API}/analyses?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch analyses: ${error.message}`);
    }
  }
};

export default apiService;