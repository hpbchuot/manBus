import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Box, CircularProgress, Typography } from '@mui/material';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
  requireDriver?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requireAdmin = false,
  requireDriver = false 
}) => {
  const { isAuthenticated, user, isLoading } = useAuth();

  // Đang kiểm tra trạng thái authentication
  if (isLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="body1" color="text.secondary">
          Đang xác thực...
        </Typography>
      </Box>
    );
  }

  // Chưa đăng nhập
  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // Kiểm tra quyền Admin
  if (requireAdmin && user?.role !== 'admin') {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          gap: 2,
          p: 3,
        }}
      >
        <Typography variant="h5" color="error" fontWeight={600}>
          Truy cập bị từ chối
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Bạn không có quyền truy cập trang này. Vui lòng liên hệ quản trị viên.
        </Typography>
      </Box>
    );
  }

  // Kiểm tra quyền Driver
  if (requireDriver && user?.role !== 'driver' && user?.role !== 'admin') {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          gap: 2,
          p: 3,
        }}
      >
        <Typography variant="h5" color="error" fontWeight={600}>
          Truy cập bị từ chối
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Chỉ tài xế mới có thể truy cập trang này.
        </Typography>
      </Box>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;