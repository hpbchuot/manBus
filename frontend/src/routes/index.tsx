import React from 'react';
import { Routes, Route } from 'react-router-dom';
import MainLayout from '@/layouts/MainLayout';
import HomePage from '@/pages/HomePage';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const AdminDashboard = React.lazy(() => import('@/pages/admin/AdminDashboard'));
const DriverDashboard = React.lazy(() => import('@/pages/driver/DriverDashboard'));

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
      </Route>

      {/* Protected Routes - Admin Only */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute requireAdmin>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={
            <React.Suspense fallback={<div>Loading...</div>}>
              <AdminDashboard />
            </React.Suspense>
          }
        />
      </Route>

      {/* Protected Routes - Driver Only */}
      <Route
        path="/driver"
        element={
          <ProtectedRoute requireDriver>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route
          index
          element={
            <React.Suspense fallback={<div>Loading...</div>}>
              <DriverDashboard />
            </React.Suspense>
          }
        />
      </Route>
    </Routes>
  );
};