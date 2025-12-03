import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import { Box, Typography, Chip, Divider } from '@mui/material';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus';
import type { Stop } from '@/types/stop';
import { busStopIcon, selectedBusStopIcon } from '@/utils/mapIcons';

interface StopMarkerProps {
  stop: Stop;
  isSelected?: boolean;
  routes?: Array<{ id: number; name: string }>; // Các tuyến đi qua stop này
  onClick?: (stop: Stop) => void;
}

const StopMarker: React.FC<StopMarkerProps> = ({ 
  stop, 
  isSelected = false,
  routes = [],
  onClick 
}) => {
  const handleClick = () => {
    onClick?.(stop);
  };

  return (
    <Marker
      position={[stop.latitude, stop.longitude]}
      icon={isSelected ? selectedBusStopIcon : busStopIcon}
      eventHandlers={{
        click: handleClick,
      }}
    >
      <Popup maxWidth={300} closeButton={true}>
        <Box sx={{ p: 1, minWidth: 250 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 2 }}>
            <LocationOnIcon sx={{ color: 'primary.main', mt: 0.5 }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 0.5 }}>
                {stop.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                ID: {stop.id}
              </Typography>
            </Box>
          </Box>

          {/* Coordinates */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="caption" color="text.secondary">
              Tọa độ: {stop.latitude.toFixed(5)}, {stop.longitude.toFixed(5)}
            </Typography>
          </Box>

          {/* Routes passing through this stop */}
          {routes.length > 0 && (
            <>
              <Divider sx={{ my: 1.5 }} />
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <DirectionsBusIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                  <Typography variant="caption" fontWeight={600} color="text.secondary">
                    Các tuyến đi qua ({routes.length})
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {routes.map((route) => (
                    <Chip
                      key={route.id}
                      label={route.name}
                      size="small"
                      sx={{
                        bgcolor: 'primary.main',
                        color: 'white',
                        fontWeight: 600,
                        fontSize: '0.7rem',
                      }}
                    />
                  ))}
                </Box>
              </Box>
            </>
          )}
        </Box>
      </Popup>
    </Marker>
  );
};

export default StopMarker;