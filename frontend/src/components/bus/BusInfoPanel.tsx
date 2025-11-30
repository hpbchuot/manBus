import React from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Button,
  Divider,
  CircularProgress,
  Stack,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import RouteIcon from '@mui/icons-material/Route';
import UpdateIcon from '@mui/icons-material/Update';
import { useBus, useRoute } from '@/hooks/useBusData';
import BusStatusBadge from './BusStatusBadge';
import { formatDistanceToNow } from 'date-fns';
import { vi } from 'date-fns/locale';

interface BusInfoPanelProps {
  busId: number;
  onClose?: () => void;
  onTrackBus?: (busId: number) => void;
  onViewRoute?: (routeId: number) => void;
}

const BusInfoPanel: React.FC<BusInfoPanelProps> = ({
  busId,
  onClose,
  onTrackBus,
  onViewRoute,
}) => {
  const { data: bus, isLoading, isError } = useBus(busId);
  const { data: route } = useRoute(bus?.routeId || 0);

  if (isLoading) {
    return (
      <Paper
        elevation={3}
        sx={{
          position: 'absolute',
          right: 16,
          top: 80,
          width: 320,
          zIndex: 1000,
          borderRadius: 2,
          p: 3,
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Paper>
    );
  }

  if (isError || !bus) {
    return (
      <Paper
        elevation={3}
        sx={{
          position: 'absolute',
          right: 16,
          top: 80,
          width: 320,
          zIndex: 1000,
          borderRadius: 2,
          p: 3,
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1" fontWeight={700} color="error">
            Lỗi tải thông tin
          </Typography>
          <IconButton size="small" onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>
        <Typography variant="body2" color="text.secondary">
          Không thể tải thông tin xe bus. Vui lòng thử lại.
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper
      elevation={3}
      sx={{
        position: 'absolute',
        right: 16,
        top: 80,
        width: 320,
        maxHeight: 'calc(100vh - 100px)',
        zIndex: 1000,
        borderRadius: 2,
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          bgcolor: 'primary.main',
          color: 'white',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <DirectionsBusIcon />
          <Typography variant="subtitle1" fontWeight={700}>
            Thông tin xe bus
          </Typography>
        </Box>
        <IconButton size="small" onClick={onClose} sx={{ color: 'white' }}>
          <CloseIcon />
        </IconButton>
      </Box>

      {/* Bus Information */}
      <Box sx={{ p: 2 }}>
        <Stack spacing={2}>
          {/* Bus Name */}
          <Box>
            <Typography variant="caption" color="text.secondary" display="block">
              Tên xe
            </Typography>
            <Typography variant="h6" fontWeight={600}>
              {bus.name}
            </Typography>
          </Box>

          {/* Plate Number */}
          <Box>
            <Typography variant="caption" color="text.secondary" display="block">
              Biển số
            </Typography>
            <Typography variant="body1" fontWeight={500}>
              {bus.plateNumber}
            </Typography>
          </Box>

          {/* Status */}
          <Box>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.5 }}>
              Trạng thái
            </Typography>
            <BusStatusBadge status={bus.status} size="medium" />
          </Box>

          {/* Route */}
          {bus.routeName && (
            <Box>
              <Typography variant="caption" color="text.secondary" display="block">
                Tuyến đường
              </Typography>
              <Typography variant="body1" fontWeight={500}>
                {bus.routeName}
              </Typography>
              {route && route.stopCount && (
                <Typography variant="caption" color="text.secondary">
                  {route.stopCount} điểm dừng
                </Typography>
              )}
            </Box>
          )}

          {/* Model (if available) */}
          {bus.model && (
            <Box>
              <Typography variant="caption" color="text.secondary" display="block">
                Dòng xe
              </Typography>
              <Typography variant="body2">{bus.model}</Typography>
            </Box>
          )}

          {/* Last Updated */}
          {bus.lastUpdated && (
            <Box>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 0.5 }}>
                Cập nhật lần cuối
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <UpdateIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                <Typography variant="caption" color="text.secondary">
                  {formatDistanceToNow(new Date(bus.lastUpdated), {
                    addSuffix: true,
                    locale: vi,
                  })}
                </Typography>
              </Box>
            </Box>
          )}
        </Stack>

        <Divider sx={{ my: 2 }} />

        {/* Action Buttons */}
        <Stack spacing={1}>
          {bus.currentLocation && (
            <Button
              fullWidth
              variant="contained"
              startIcon={<MyLocationIcon />}
              onClick={() => onTrackBus?.(bus.busId)}
              sx={{ borderRadius: 2 }}
            >
              Theo dõi xe bus
            </Button>
          )}

          {bus.routeId && (
            <Button
              fullWidth
              variant="outlined"
              startIcon={<RouteIcon />}
              onClick={() => onViewRoute?.(bus.routeId!)}
              sx={{ borderRadius: 2 }}
            >
              Xem tuyến đường
            </Button>
          )}
        </Stack>

        {/* Location Status */}
        {!bus.currentLocation && (
          <Box sx={{ mt: 2, p: 1.5, bgcolor: 'warning.lighter', borderRadius: 1 }}>
            <Typography variant="caption" color="warning.dark">
              Vị trí xe bus chưa được cập nhật
            </Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default BusInfoPanel;
