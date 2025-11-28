import { useState, useCallback } from 'react';

interface AsyncState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

// Hook Generic áp dụng cho mọi API call
export const useAsync = <T, P = any>(
  asyncFunction: (params: P) => Promise<T>,
  immediate = false
) => {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    isLoading: immediate,
    error: null,
  });

  // Template Method: Định nghĩa khung sườn của quy trình xử lý bất đồng bộ
  const execute = useCallback(
    async (params: P) => {
      setState((prevState) => ({ ...prevState, isLoading: true, error: null }));
      
      try {
        const response = await asyncFunction(params);
        setState({ data: response, isLoading: false, error: null });
        return response;
      } catch (error: any) {
        const message = error.message || 'Đã có lỗi xảy ra';
        setState({ data: null, isLoading: false, error: message });
        throw error; // Ném lỗi tiếp để Component có thể catch nếu muốn xử lý riêng
      }
    },
    [asyncFunction]
  );

  return { ...state, execute };
};