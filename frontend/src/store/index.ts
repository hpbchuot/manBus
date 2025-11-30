import { configureStore } from '@reduxjs/toolkit';
import {type TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import authReducer from './slices/authSlice';
import busReducer from './slices/busSlice';
import mapReducer from './slices/mapSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    bus: busReducer,
    map: mapReducer,
  },
});

// Types cho TypeScript dùng trong App
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch: () => AppDispatch = useDispatch;
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;