import React from 'react';
import { Box, Typography, Container, Paper, Button, Chip } from '@mui/material';
import { useAuth } from '@/hooks/useAuth';
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import RouteIcon from '@mui/icons-material/Route';

const DriverDashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Dashboard Tài Xế
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Xin chào, {user?.fullName}!
        </Typography>
      </Box>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <DirectionsBusIcon color="primary" sx={{ fontSize: 40 }} />
          <Box sx={{ flexGrow: 1 }}>
            <Typography variant="h6" fontWeight={600}>
              Xe buýt của bạn
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Biển số: 29B-12345
            </Typography>
          </Box>
          <Chip label="Hoạt động" color="success" />
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
          <RouteIcon color="primary" />
          <Box>
            <Typography variant="body2" fontWeight={600}>
              Tuyến 01
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Bến xe Miền Đông - Chợ Bến Thành
            </Typography>
          </Box>
        </Box>

        <Button
          variant="contained"
          fullWidth
          startIcon={<LocationOnIcon />}
          size="large"
          sx={{ borderRadius: 2 }}
        >
          Bắt đầu hành trình
        </Button>
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Thông tin hành trình hôm nay
        </Typography>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="body2" color="text.secondary">
            Số chuyến hoàn thành
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            8 chuyến
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 2, borderBottom: 1, borderColor: 'divider' }}>
          <Typography variant="body2" color="text.secondary">
            Quãng đường
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            120 km
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', py: 2 }}>
          <Typography variant="body2" color="text.secondary">
            Thời gian lái xe
          </Typography>
          <Typography variant="body1" fontWeight={600}>
            6 giờ 30 phút
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default DriverDashboard;