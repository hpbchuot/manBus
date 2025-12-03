import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Button,
  CircularProgress,
  Chip,
} from '@mui/material';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import DirectionsWalkIcon from '@mui/icons-material/DirectionsWalk';
import type { NearestStop } from '@/types/stop';
import { StopService } from '@/services/api/stopApi';
import api from '@/services/api';
import { toast } from 'react-toastify';

interface NearestStopsPanelProps {
  onStopSelect?: (stopId: number) => void;
}

const NearestStopsPanel: React.FC<NearestStopsPanelProps> = ({ onStopSelect }) => {
  const [nearestStops, setNearestStops] = useState<NearestStop[]>([]);
  const [loading, setLoading] = useState(false);
  // const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null);

  const stopService = new StopService(api);

  const handleFindNearestStops = () => {
    if (!navigator.geolocation) {
      toast.error('Trình duyệt không hỗ trợ định vị');
      return;
    }

    setLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        // setUserLocation({ lat: latitude, lng: longitude });

        try {
          const stops = await stopService.findNearestStops(
            latitude,
            longitude,
            2000, // 2km radius
            10 // Top 10 nearest
          );
          setNearestStops(stops);
          
          if (stops.length === 0) {
            toast.info('Không tìm thấy điểm dừng nào gần bạn');
          } else {
            toast.success(`Tìm thấy ${stops.length} điểm dừng gần bạn`);
          }
        } catch (err: any) {
          const message = err.response?.data?.message || 'Không thể tìm điểm dừng gần bạn';
          toast.error(message);
        } finally {
          setLoading(false);
        }
      },
      (error) => {
        setLoading(false);
        toast.error('Không thể lấy vị trí của bạn. Vui lòng bật GPS.');
        console.error('Geolocation error:', error);
      }
    );
  };

  const formatDistance = (meters: number): string => {
    if (meters < 1000) {
      return `${Math.round(meters)}m`;
    }
    return `${(meters / 1000).toFixed(1)}km`;
  };

  return (
    <Paper
      elevation={3}
      sx={{
        position: 'absolute',
        right: 16,
        bottom: 100,
        width: 320,
        maxHeight: 400,
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
        <Typography variant="subtitle1" fontWeight={700}>
          Điểm dừng gần bạn
        </Typography>
      </Box>

      {/* Find Button */}
      <Box sx={{ p: 2 }}>
        <Button
          fullWidth
          variant="contained"
          startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <MyLocationIcon />}
          onClick={handleFindNearestStops}
          disabled={loading}
          sx={{ borderRadius: 2 }}
        >
          {loading ? 'Đang tìm kiếm...' : 'Tìm điểm dừng gần tôi'}
        </Button>
      </Box>

      {/* Results List */}
      {nearestStops.length > 0 && (
        <List
          sx={{
            flexGrow: 1,
            overflowY: 'auto',
            p: 0,
            '&::-webkit-scrollbar': {
              width: '6px',
            },
            '&::-webkit-scrollbar-thumb': {
              backgroundColor: 'rgba(0,0,0,0.2)',
              borderRadius: '3px',
            },
          }}
        >
          {nearestStops.map((stop, index) => (
            <ListItem
              key={stop.id}
              disablePadding
              sx={{
                borderBottom: index < nearestStops.length - 1 ? 1 : 0,
                borderColor: 'divider',
              }}
            >
              <ListItemButton onClick={() => onStopSelect?.(stop.id)}>
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <LocationOnIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>
                      {stop.name}
                    </Typography>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <DirectionsWalkIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                      <Typography variant="caption" color="text.secondary">
                        {formatDistance(stop.distanceMeters)}
                      </Typography>
                    </Box>
                  }
                />
                <Chip
                  label={`#${index + 1}`}
                  size="small"
                  sx={{ bgcolor: 'primary.main', color: 'white', fontWeight: 700 }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      )}

      {/* Empty State */}
      {!loading && nearestStops.length === 0 && (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Nhấn nút trên để tìm điểm dừng gần bạn
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default NearestStopsPanel;