import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const recordingAPI = {
  // Upload and process recording
  upload: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/api/recordings/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress && onProgress(percentCompleted);
      },
    });
  },

  // Get all recordings
  getAll: (params = {}) => {
    return api.get('/api/recordings', { params });
  },

  // Get recording by ID
  getById: (id) => {
    return api.get(`/api/recordings/${id}`);
  },

  // Update recording
  update: (id, data) => {
    return api.put(`/api/recordings/${id}`, data);
  },

  // Delete recording
  delete: (id) => {
    return api.delete(`/api/recordings/${id}`);
  },

  // Get processing status
  getStatus: (id) => {
    return api.get(`/api/recordings/${id}/status`);
  },

  // Download file
  download: (id, type) => {
    return api.get(`/api/recordings/${id}/download/${type}`, {
      responseType: 'blob',
    });
  },
};

export const transcriptionAPI = {
  // Get transcription
  get: (recordingId) => {
    return api.get(`/api/transcriptions/${recordingId}`);
  },

  // Update transcription
  update: (recordingId, data) => {
    return api.put(`/api/transcriptions/${recordingId}`, data);
  },
};

export const summaryAPI = {
  // Generate summary
  generate: (recordingId, options = {}) => {
    return api.post(`/api/summaries/generate`, {
      recording_id: recordingId,
      ...options,
    });
  },

  // Get summary
  get: (recordingId) => {
    return api.get(`/api/summaries/${recordingId}`);
  },

  // Update summary
  update: (recordingId, data) => {
    return api.put(`/api/summaries/${recordingId}`, data);
  },
};

export const testAPI = {
  // Generate test
  generate: (recordingId, options = {}) => {
    return api.post(`/api/tests/generate`, {
      recording_id: recordingId,
      ...options,
    });
  },

  // Get test
  get: (recordingId) => {
    return api.get(`/api/tests/${recordingId}`);
  },

  // Submit test answers
  submit: (testId, answers) => {
    return api.post(`/api/tests/${testId}/submit`, { answers });
  },
};

export const searchAPI = {
  // Semantic search
  semantic: (query, filters = {}) => {
    return api.post('/api/search/semantic', {
      query,
      filters,
    });
  },

  // Full-text search
  fulltext: (query, filters = {}) => {
    return api.post('/api/search/fulltext', {
      query,
      filters,
    });
  },

  // Get similar recordings
  similar: (recordingId, limit = 10) => {
    return api.get(`/api/search/similar/${recordingId}`, {
      params: { limit },
    });
  },
};

export const analyticsAPI = {
  // Get dashboard data
  getDashboard: () => {
    return api.get('/api/analytics/dashboard');
  },

  // Get usage statistics
  getUsage: (period = '30d') => {
    return api.get('/api/analytics/usage', {
      params: { period },
    });
  },

  // Get trends
  getTrends: (metric, period = '30d') => {
    return api.get('/api/analytics/trends', {
      params: { metric, period },
    });
  },
};

export const knowledgeGraphAPI = {
  // Get knowledge graph for recording
  get: (recordingId) => {
    return api.get(`/api/knowledge-graph/${recordingId}`);
  },

  // Query knowledge graph
  query: (query, recordingId = null) => {
    return api.post('/api/knowledge-graph/query', {
      query,
      recording_id: recordingId,
    });
  },

  // Get entity relationships
  getRelationships: (entityId) => {
    return api.get(`/api/knowledge-graph/relationships/${entityId}`);
  },
};

export const webResearchAPI = {
  // Enhance content with web research
  enhance: (recordingId, topics = []) => {
    return api.post('/api/web-research/enhance', {
      recording_id: recordingId,
      topics,
    });
  },

  // Get research results
  get: (recordingId) => {
    return api.get(`/api/web-research/${recordingId}`);
  },
};

// Simplified API functions for easier component usage
export const apiHelpers = {
  // Get all recordings (simplified)
  getRecordings: async () => {
    try {
      const response = await recordingAPI.getAll();
      return response.data;
    } catch (error) {
      console.error('Failed to fetch recordings:', error);
      throw error;
    }
  },

  // Get single recording (simplified)
  getRecording: async (id) => {
    try {
      const response = await recordingAPI.getById(id);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch recording:', error);
      throw error;
    }
  },

  // Upload recording (simplified)
  uploadRecording: async (file, onProgress) => {
    try {
      const response = await recordingAPI.upload(file, onProgress);
      return response.data;
    } catch (error) {
      console.error('Failed to upload recording:', error);
      throw error;
    }
  },

  // Semantic search (simplified)
  semanticSearch: async (query) => {
    try {
      const response = await searchAPI.semantic(query);
      return response.data;
    } catch (error) {
      console.error('Semantic search failed:', error);
      throw error;
    }
  },

  // Get analytics (simplified)
  getAnalytics: async () => {
    try {
      const response = await analyticsAPI.getDashboard();
      return response.data;
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      throw error;
    }
  },

  // Generate test (simplified)
  generateTest: async (recordingId, options = {}) => {
    try {
      const response = await testAPI.generate(recordingId, options);
      return response.data;
    } catch (error) {
      console.error('Failed to generate test:', error);
      throw error;
    }
  },

  // Process recording (simplified)
  processRecording: async (recordingId) => {
    try {
      // This would trigger the full processing pipeline
      const response = await api.post(`/api/recordings/${recordingId}/process`);
      return response.data;
    } catch (error) {
      console.error('Failed to process recording:', error);
      throw error;
    }
  },
};

// Export simplified API as default for easier imports
export const apiSimple = apiHelpers;

export default api;
