import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import { Box, Typography, Chip, Divider } from '@mui/material';
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus';
import RouteIcon from '@mui/icons-material/Route';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import type { Bus } from '@/types/bus';
import { busIcon, selectedBusIcon, trackedBusIcon } from '@/utils/mapIcons';

interface BusMarkerProps {
  bus: Bus;
  isSelected?: boolean;
  isTracked?: boolean;
  onClick?: (bus: Bus) => void;
}

const BusMarker: React.FC<BusMarkerProps> = ({
  bus,
  isSelected = false,
  isTracked = false,
  onClick,
}) => {
  const handleClick = () => {
    onClick?.(bus);
  };

  // Determine which icon to use based on state
  const getIcon = () => {
    if (isTracked) return trackedBusIcon;
    if (isSelected) return selectedBusIcon;
    return busIcon;
  };

  // Only render if bus has a current location
  if (!bus.currentLocation) {
    return null;
  }

  // Format last updated time
  const getLastUpdated = () => {
    if (!bus.lastUpdated) return 'Unknown';

    const now = new Date();
    const updated = new Date(bus.lastUpdated);
    const diffMs = now.getTime() - updated.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins === 1) return '1 minute ago';
    if (diffMins < 60) return `${diffMins} minutes ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours === 1) return '1 hour ago';
    return `${diffHours} hours ago`;
  };

  // Get status color
  const getStatusColor = () => {
    switch (bus.status) {
      case 'Active':
        return 'success';
      case 'Maintenance':
        return 'warning';
      case 'Inactive':
      default:
        return 'default';
    }
  };

  return (
    <Marker
      position={[bus.currentLocation.latitude, bus.currentLocation.longitude]}
      icon={getIcon()}
      eventHandlers={{
        click: handleClick,
      }}
    >
      <Popup maxWidth={300} closeButton={true}>
        <Box sx={{ p: 1, minWidth: 250 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 2 }}>
            <DirectionsBusIcon sx={{ color: 'primary.main', mt: 0.5 }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 0.5 }}>
                {bus.name || bus.plateNumber}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {bus.plateNumber}
              </Typography>
            </Box>
            <Chip
              label={bus.status}
              color={getStatusColor()}
              size="small"
              sx={{ fontWeight: 600 }}
            />
          </Box>

          {/* Bus Details */}
          <Box sx={{ mb: 2 }}>
            {bus.model && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                Model: {bus.model}
              </Typography>
            )}
            <Typography variant="caption" color="text.secondary">
              Location: {bus.currentLocation.latitude.toFixed(5)}, {bus.currentLocation.longitude.toFixed(5)}
            </Typography>
          </Box>

          {/* Route Information */}
          {bus.routeName && (
            <>
              <Divider sx={{ my: 1.5 }} />
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <RouteIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                  <Typography variant="caption" fontWeight={600} color="text.secondary">
                    Route
                  </Typography>
                </Box>
                <Chip
                  label={bus.routeName}
                  size="small"
                  sx={{
                    bgcolor: 'primary.main',
                    color: 'white',
                    fontWeight: 600,
                  }}
                />
              </Box>
            </>
          )}

          {/* Last Updated */}
          <Divider sx={{ my: 1.5 }} />
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AccessTimeIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
            <Typography variant="caption" color="text.secondary">
              Updated: {getLastUpdated()}
            </Typography>
          </Box>

          {/* Tracking State Indicator */}
          {isTracked && (
            <Box sx={{ mt: 1.5, pt: 1.5, borderTop: '1px dashed', borderColor: 'divider' }}>
              <Typography
                variant="caption"
                sx={{
                  color: 'error.main',
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                }}
              >
                <span style={{ fontSize: '16px' }}>📍</span> Tracking this bus
              </Typography>
            </Box>
          )}
        </Box>
      </Popup>
    </Marker>
  );
};

export default BusMarker;
