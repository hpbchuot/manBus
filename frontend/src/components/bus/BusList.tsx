import React, { useState, useMemo } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus';
import { useActiveBuses, useAllRoutes } from '@/hooks/useBusData';
import { useDebounce } from '@/hooks/useDebounce';
import type { Bus, BusStatus } from '@/types/bus';
import BusStatusBadge from './BusStatusBadge';

interface BusListProps {
  onBusSelect?: (bus: Bus) => void;
  selectedBusId?: number | null;
}

const BusList: React.FC<BusListProps> = ({ onBusSelect, selectedBusId }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<BusStatus | 'All'>('All');
  const [routeFilter, setRouteFilter] = useState<number | 'All'>('All');

  const debouncedSearch = useDebounce(searchQuery, 300);

  const { data: buses, isLoading, isError, error } = useActiveBuses();
  const { data: routes = [] } = useAllRoutes();

  const filteredBuses = useMemo(() => {
    let filtered = [...(buses?.buses || [])];

    // Filter by search query
    if (debouncedSearch.trim()) {
      const query = debouncedSearch.toLowerCase();
      filtered = filtered.filter(
        (bus) =>
          bus.name.toLowerCase().includes(query) ||
          bus.plateNumber.toLowerCase().includes(query) ||
          bus.busId.toString().includes(query) ||
          bus.routeName?.toLowerCase().includes(query)
      );
    }

    // Filter by status
    if (statusFilter !== 'All') {
      filtered = filtered.filter((bus) => bus.status === statusFilter);
    }

    // Filter by route
    if (routeFilter !== 'All') {
      filtered = filtered.filter((bus) => bus.routeId === routeFilter);
    }

    return filtered;
  }, [buses, debouncedSearch, statusFilter, routeFilter]);

  const handleBusClick = (bus: Bus) => {
    onBusSelect?.(bus);
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setStatusFilter('All');
    setRouteFilter('All');
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (isError) {
    return (
      <Box sx={{ p: 2 }}>
        <Alert severity="error">
          {error instanceof Error ? error.message : 'Không thể tải danh sách xe bus'}
        </Alert>
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
          placeholder="Tìm kiếm xe bus..."
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

      {/* Filters */}
      <Box sx={{ p: 2, bgcolor: 'background.default', borderBottom: 1, borderColor: 'divider' }}>
        <Stack spacing={1.5}>
          {/* Status Filter */}
          <FormControl size="small" fullWidth>
            <InputLabel>Trạng thái</InputLabel>
            <Select
              value={statusFilter}
              label="Trạng thái"
              onChange={(e) => setStatusFilter(e.target.value as BusStatus | 'All')}
            >
              <MenuItem value="All">Tất cả</MenuItem>
              <MenuItem value="Active">Hoạt động</MenuItem>
              <MenuItem value="Inactive">Không hoạt động</MenuItem>
              <MenuItem value="Maintenance">Bảo trì</MenuItem>
            </Select>
          </FormControl>

          {/* Route Filter */}
          <FormControl size="small" fullWidth>
            <InputLabel>Tuyến đường</InputLabel>
            <Select
              value={routeFilter}
              label="Tuyến đường"
              onChange={(e) => setRouteFilter(e.target.value as number | 'All')}
            >
              <MenuItem value="All">Tất cả</MenuItem>
              {routes.map((route) => (
                <MenuItem key={route.id} value={route.id}>
                  {route.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Reset Filters Button */}
          {(statusFilter !== 'All' || routeFilter !== 'All' || searchQuery) && (
            <Typography
              variant="caption"
              color="primary"
              sx={{ cursor: 'pointer', textAlign: 'center', mt: 0.5 }}
              onClick={handleResetFilters}
            >
              Xóa bộ lọc
            </Typography>
          )}
        </Stack>
      </Box>

      {/* Results Count */}
      <Box sx={{ px: 2, py: 1, bgcolor: 'background.paper' }}>
        <Typography variant="caption" color="text.secondary">
          Tìm thấy {filteredBuses.length} xe bus
        </Typography>
      </Box>

      {/* Bus List */}
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
        {filteredBuses.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Không tìm thấy xe bus nào
            </Typography>
          </Box>
        ) : (
          filteredBuses.map((bus) => (
            <ListItem
              key={bus.busId}
              disablePadding
              sx={{
                borderBottom: 1,
                borderColor: 'divider',
                bgcolor: bus.busId === selectedBusId ? 'action.selected' : 'transparent',
              }}
            >
              <ListItemButton
                onClick={() => handleBusClick(bus)}
                sx={{
                  py: 1.5,
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <DirectionsBusIcon
                    sx={{
                      color: bus.busId === selectedBusId ? 'primary.main' : 'text.secondary',
                    }}
                  />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography
                        variant="body2"
                        fontWeight={bus.busId === selectedBusId ? 700 : 500}
                      >
                        {bus.name}
                      </Typography>
                      <BusStatusBadge status={bus.status} size="small" />
                    </Box>
                  }
                  secondary={
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        {bus.plateNumber}
                      </Typography>
                      {bus.routeName && (
                        <Typography variant="caption" color="primary.main" fontWeight={500}>
                          {bus.routeName}
                        </Typography>
                      )}
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

export default BusList;
