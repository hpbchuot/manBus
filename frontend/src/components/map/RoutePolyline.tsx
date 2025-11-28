import React, { useEffect, useState } from 'react';
import { Polyline, Popup } from 'react-leaflet';
import { Box, Typography, Chip } from '@mui/material';
import type { Route, RouteGeoJSON } from '@/types/route';
import { RouteService } from '@/services/api/routeApi';
import { RouteAdapter } from '@/services/adapters/routeAdapter';
import api from '@/services/api';

interface RoutePolylineProps {
  route: Route;
  color?: string;
  weight?: number;
  opacity?: number;
  onClick?: (route: Route) => void;
}

const RoutePolyline: React.FC<RoutePolylineProps> = ({
  route,
  color = '#00C060',
  weight = 4,
  opacity = 0.8,
  onClick,
}) => {
  const [coordinates, setCoordinates] = useState<[number, number][]>([]);
  const [loading, setLoading] = useState(true);

  const routeAdapter = new RouteAdapter();
  const routeService = new RouteService(api, routeAdapter);

  useEffect(() => {
    loadRouteGeometry();
  }, [route.id]);

  const loadRouteGeometry = async () => {
    try {
      const geoJSON: RouteGeoJSON = await routeService.getRouteGeoJSON(route.id);
      
      // Convert GeoJSON coordinates [lng, lat] to Leaflet format [lat, lng]
      const leafletCoords: [number, number][] = geoJSON.coordinates.map(
        ([lng, lat]) => [lat, lng]
      );
      
      setCoordinates(leafletCoords);
    } catch (err) {
      console.error('Error loading route geometry:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClick = () => {
    onClick?.(route);
  };

  if (loading || coordinates.length === 0) {
    return null;
  }

  return (
    <Polyline
      positions={coordinates}
      color={color}
      weight={weight}
      opacity={opacity}
      eventHandlers={{
        click: handleClick,
      }}
    >
      <Popup>
        <Box sx={{ p: 1, minWidth: 200 }}>
          <Typography variant="subtitle2" fontWeight={700} sx={{ mb: 1 }}>
            {route.name}
          </Typography>
          
          {route.stopCount && (
            <Chip
              label={`${route.stopCount} điểm dừng`}
              size="small"
              sx={{ mr: 1, mb: 0.5 }}
            />
          )}
          
          {route.lengthMeters && (
            <Chip
              label={`${(route.lengthMeters / 1000).toFixed(1)} km`}
              size="small"
              color="primary"
            />
          )}
        </Box>
      </Popup>
    </Polyline>
  );
};

export default RoutePolyline;