import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = import.meta.env.VITE_API_URL || 'https://quotmate-backend.onrender.com/api';

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export function getApiErrorMessage(error, fallback = 'Something went wrong') {
  const detail = error?.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail.map((item) => item?.msg).filter(Boolean).join(', ') || fallback;
  }

  if (typeof detail === 'string') {
    return detail;
  }

  return error?.message || fallback;
}

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      const isAuthPage =
        window.location.pathname.includes('/login') ||
        window.location.pathname.includes('/register');

      if (!isAuthPage) {
        window.location.href = '/login';
        toast.error('Session expired. Please login again.');
      }
    } else if (error.response?.status === 500) {
      toast.error('Server error. Please try again later.');
    }

    return Promise.reject(error);
  }
);

// Auth APIs
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data),
  uploadLogo: (formData) =>
    api.post('/auth/upload-logo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// OCR APIs
export const ocrAPI = {
  upload: (formData) => api.post('/ocr/extract', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  }),
  extract: (formData) => api.post('/ocr/extract', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  }),
  processBase64: (data) => api.post('/ocr/process-base64', data, { timeout: 120000 }),
  health: () => api.get('/ocr/health'),
};

// Quotation APIs
export const quotationAPI = {
  create: (data) => api.post('/quotations', data),
  list: (params) => api.get('/quotations', { params }),
  get: (id) => api.get(`/quotations/${id}`),
  update: (id, data) => api.put(`/quotations/${id}`, data),
  delete: (id) => api.delete(`/quotations/${id}`),
  fromOCR: (data) => api.post('/quotations/from-ocr', data, { timeout: 120000 }),
  calculate: (data) => api.post('/quotations/calculate', data),
  finalize: (id) => api.post(`/quotations/${id}/finalize`),
  revertFinalize: (id) => api.post(`/quotations/${id}/revert-finalize`),
  download: (id) => api.get(`/quotations/${id}/download`, { responseType: 'blob' }),
};

// Product APIs
export const productAPI = {
  create: (data) => api.post('/products', data),
  list: (params) => api.get('/products', { params }),
  get: (id) => api.get(`/products/${id}`),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
};

// MOM APIs
export const momAPI = {
  create: (data) => api.post('/moms', data),
  summarize: (data) => api.post('/moms/summarize', data),
  list: (params) => api.get('/moms', { params }),
  get: (id) => api.get(`/moms/${id}`),
  update: (id, data) => api.put(`/moms/${id}`, data),
  delete: (id) => api.delete(`/moms/${id}`),
  createActionItem: (momId, data) => api.post(`/moms/${momId}/action-items`, data),
  updateActionItem: (momId, actionItemId, data) =>
    api.put(`/moms/${momId}/action-items/${actionItemId}`, data),
  deleteActionItem: (momId, actionItemId) =>
    api.delete(`/moms/${momId}/action-items/${actionItemId}`),
  finalize: (id) => api.post(`/moms/${id}/finalize`),
  revertFinalize: (id) => api.post(`/moms/${id}/revert-finalize`),
  download: (id) => api.get(`/moms/${id}/download`, { responseType: 'blob' }),
};

// Work Order APIs
export const workOrderAPI = {
  create: (data) => api.post('/work-orders', data),
  list: (params) => api.get('/work-orders', { params }),
  get: (id) => api.get(`/work-orders/${id}`),
  update: (id, data) => api.put(`/work-orders/${id}`, data),
  delete: (id) => api.delete(`/work-orders/${id}`),
  finalize: (id) => api.post(`/work-orders/${id}/finalize`),
  revertFinalize: (id) => api.post(`/work-orders/${id}/revert-finalize`),
  calculate: (data) => api.post('/work-orders/calculate', data),
  download: (id) => api.get(`/work-orders/${id}/download`, { responseType: 'blob' }),
  fromOCR: (data) => api.post('/work-orders/from-ocr', data, { timeout: 120000 }),

  // Materials
  addMaterial: (id, data) => api.post(`/work-orders/${id}/materials`, data),
  updateMaterial: (id, materialId, data) => api.put(`/work-orders/${id}/materials/${materialId}`, data),
  deleteMaterial: (id, materialId) => api.delete(`/work-orders/${id}/materials/${materialId}`),

  // Photo upload
  uploadPhoto: (id, photoType, formData) =>
    api.post(`/work-orders/${id}/upload-photo?photo_type=${photoType}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  // Signature upload
  uploadSignature: (id, formData) =>
    api.post(`/work-orders/${id}/upload-signature`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

export const dashboardAPI = {
  getStats: () => api.get('/dashboard'),
};

export const documentsAPI = {
  search: (params) => api.get('/documents', { params }),
  delete: (id) => api.delete(`/documents/${id}`),
};

export default api;
