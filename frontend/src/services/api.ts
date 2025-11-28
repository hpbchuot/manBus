// src/services/api.ts
import axios, { 
  type AxiosError, 
  type AxiosInstance, 
  type AxiosResponse 
} from 'axios';

const BASE_URL = process.env.PUBLIC_API_URL || 'http://localhost:8000/api';

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  
  withCredentials: true, 
});


api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => Promise.reject(error)
);

// --- RESPONSE INTERCEPTOR ---
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data;
  },
  (error: AxiosError) => {
    if (error.response) {
      // Nếu lỗi 401 (Unauthorized) -> Cookie hết hạn hoặc không hợp lệ
      if (error.response.status === 401) {
        // Xóa thông tin user lưu tạm ở client
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Generic API Response wrapper
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status?: string;
}

export { storage } from './storage';
export default api;