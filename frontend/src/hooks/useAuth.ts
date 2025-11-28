import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from './store';
import { login as loginAction, logout as logoutAction, clearError } from '@/features/auth/authSlice';
import type { LoginPayload } from '@/types/auth';
import { toast } from 'react-toastify';

export const useAuth = () => {
  const dispatch = useAppDispatch();
  
  // Lấy state từ Redux
  const { user, token, isLoading, error } = useAppSelector((state) => state.auth);

  // Wrapper hàm Login
  const login = useCallback(async (payload: LoginPayload) => {
    try {
      // unwrap() giúp bắt lỗi ngay tại đây nếu thunk bị rejected
      await dispatch(loginAction(payload)).unwrap();
      // Toast success có thể đặt ở đây hoặc trong component
    } catch (err: any) {
      toast.error(err || 'Đăng nhập thất bại');
    }
  }, [dispatch]);

  // Wrapper hàm Logout
  const logout = useCallback(() => {
    dispatch(logoutAction());
    toast.info('Đã đăng xuất');
  }, [dispatch]);

  // Wrapper hàm xóa lỗi
  const resetError = useCallback(() => {
    dispatch(clearError());
  }, [dispatch]);

  return {
    user,
    token,
    isAuthenticated: !!user, // Helper boolean tiện lợi
    isLoading,
    error,
    login,
    logout,
    resetError,
  };
};