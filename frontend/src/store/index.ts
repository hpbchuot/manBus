import { configureStore } from '@reduxjs/toolkit';
import {type TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

export const store = configureStore({
  reducer: {
    
    // Sau này sẽ thêm busReducer, mapReducer ở đây
  },
});

// Types cho TypeScript dùng trong App
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Hooks custom (Dùng cái này thay vì useDispatch/useSelector gốc để có gợi ý code)
export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;