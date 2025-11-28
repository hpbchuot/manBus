import React from 'react';
import { Box, Typography, Container, Paper, Grid } from '@mui/material';
import { useAuth } from '@/hooks/useAuth';

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        Dashboard Quản Trị
      </Typography>
      
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Xin chào, {user?.fullName}!
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color="primary.main" fontWeight={700}>
              24
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Tuyến xe hoạt động
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color="primary.main" fontWeight={700}>
              156
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Xe buýt đang vận hành
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color="primary.main" fontWeight={700}>
              89
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Tài xế hoạt động
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color="primary.main" fontWeight={700}>
              2.5K
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Người dùng đăng ký
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Tính năng đang phát triển
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Quản lý tuyến xe, xe buýt, tài xế, người dùng, thống kê...
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default AdminDashboard;