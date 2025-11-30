import React, { useState, useEffect } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  TextField,
  InputAdornment,
  CircularProgress,
  Alert,
  // Chip,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import type { Stop } from '@/types/stop';
import { StopService } from '@/services/api/stopApi';
import { StopAdapter } from '@/services/adapters/stopAdapter';
import api from '@/services/api';

interface StopsListProps {
  onStopSelect?: (stop: Stop) => void;
  selectedStopId?: number | null;
}

const StopsList: React.FC<StopsListProps> = ({ onStopSelect, selectedStopId }) => {
  const [stops, setStops] = useState<Stop[]>([]);
  const [filteredStops, setFilteredStops] = useState<Stop[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const stopAdapter = new StopAdapter();
  const stopService = new StopService(api, stopAdapter);

  useEffect(() => {
    loadStops();
  }, []);

  useEffect(() => {
    filterStops();
  }, [searchQuery, stops]);

  const loadStops = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await stopService.getAllStops();
      setStops(data);
      setFilteredStops(data);
    } catch (err: any) {
      const message = err.response?.data?.message || 'Không thể tải danh sách điểm dừng';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const filterStops = () => {
    if (!searchQuery.trim()) {
      setFilteredStops(stops);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = stops.filter((stop) =>
      stop.name.toLowerCase().includes(query) ||
      stop.id.toString().includes(query)
    );
    setFilteredStops(filtered);
  };

  const handleStopClick = (stop: Stop) => {
    onStopSelect?.(stop);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Search Bar */}
      <Box sx={{ p: 2, bgcolor: 'background.paper', borderBottom: 1, borderColor: 'divider' }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Tìm kiếm điểm dừng..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon sx={{ color: 'text.secondary' }} />
              </InputAdornment>
            ),
          }}
          sx={{ bgcolor: 'background.default' }}
        />
      </Box>

      {/* Results Count */}
      <Box sx={{ px: 2, py: 1, bgcolor: 'background.default' }}>
        <Typography variant="caption" color="text.secondary">
          Tìm thấy {filteredStops.length} điểm dừng
        </Typography>
      </Box>

      {/* Stops List */}
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
        {filteredStops.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Không tìm thấy điểm dừng nào
            </Typography>
          </Box>
        ) : (
          filteredStops.map((stop) => (
            <ListItem
              key={stop.id}
              disablePadding
              sx={{
                borderBottom: 1,
                borderColor: 'divider',
                bgcolor: stop.id === selectedStopId ? 'action.selected' : 'transparent',
              }}
            >
              <ListItemButton
                onClick={() => handleStopClick(stop)}
                sx={{
                  py: 1.5,
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <LocationOnIcon
                    sx={{
                      color: stop.id === selectedStopId ? 'primary.main' : 'text.secondary',
                    }}
                  />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography
                      variant="body2"
                      fontWeight={stop.id === selectedStopId ? 700 : 500}
                      sx={{ mb: 0.5 }}
                    >
                      {stop.name}
                    </Typography>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        ID: {stop.id}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {stop.location.latitude.toFixed(5)}, {stop.location.longitude.toFixed(5)}
                      </Typography>
                    </Box>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))
        )}
      </List>
    </Box>
  );
};

export default StopsList;