import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, ZoomControl, useMap } from 'react-leaflet';
import { Box, ToggleButtonGroup, ToggleButton, Paper } from '@mui/material';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import RouteIcon from '@mui/icons-material/Route';
import DirectionsBusIcon from '@mui/icons-material/DirectionsBus';
import { MAP_CONFIG } from '@/config/mapConfig';
import StopsLayer from './StopsLayer';
import BusLayer from './BusLayer';
import RoutePolyline from './RoutePolyline';
import MapControlsWrapper from './MapControlsWrapper';
import { useActiveBuses } from '@/hooks/useBusData';
import type { Stop } from '@/types/stop';
import type { Route } from '@/types/route';
import type { Bus } from '@/types/bus';
import L from 'leaflet';

// Fix lỗi icon mặc định của Leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

// Component xử lý Resize
const MapReSizer = () => {
  const map = useMap();

  useEffect(() => {
    const resizeObserver = new ResizeObserver(() => {
      map.invalidateSize();
    });

    const mapContainer = map.getContainer();
    resizeObserver.observe(mapContainer);

    return () => {
      resizeObserver.disconnect();
    };
  }, [map]);

  return null;
};

interface BusMapProps {
  selectedRoute?: Route | null;
  onStopClick?: (stop: Stop) => void;
  onRouteClick?: (route: Route) => void;
  onBusClick?: (bus: Bus) => void;
}

const BusMap: React.FC<BusMapProps> = ({
  selectedRoute = null,
  onStopClick,
  onRouteClick,
  onBusClick
}) => {
  const [layers, setLayers] = useState<string[]>([]); // Layers hiển thị - hidden by default
  const [selectedStopId, setSelectedStopId] = useState<number | null>(null);
  const [selectedStopData, setSelectedStopData] = useState<Stop | null>(null);
  const [selectedBusId, setSelectedBusId] = useState<number | null>(null);
  const [trackedBusId] = useState<number | null>(null);

  // Fetch active buses with auto-refresh every 30 seconds
  const { data: buses } = useActiveBuses();

  const handleLayerToggle = (
    _event: React.MouseEvent<HTMLElement>,
    newLayers: string[]
  ) => {
    setLayers(newLayers);
  };

  const handleStopClick = (stop: Stop) => {
    setSelectedStopId(stop.id);
    setSelectedStopData(stop);
    onStopClick?.(stop);
  };

  const handleBusClick = (bus: Bus) => {
    setSelectedBusId(bus.busId);
    onBusClick?.(bus);
  };

  return (
    <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Layer Control - Nút bật/tắt các layer */}
      <Paper
        elevation={2}
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
          zIndex: 1000,
          bgcolor: 'background.paper',
          borderRadius: 2,
        }}
      >
        <ToggleButtonGroup
          value={layers}
          onChange={handleLayerToggle}
          aria-label="map layers"
          size="small"
          orientation="vertical"
        >
          <ToggleButton value="stops" aria-label="stops">
            <LocationOnIcon fontSize="small" />
          </ToggleButton>
          <ToggleButton value="buses" aria-label="buses">
            <DirectionsBusIcon fontSize="small" />
          </ToggleButton>
          <ToggleButton value="routes" aria-label="routes">
            <RouteIcon fontSize="small" />
          </ToggleButton>
        </ToggleButtonGroup>
      </Paper>

      {/* Map Container */}
      <MapContainer
        center={MAP_CONFIG.DEFAULT_CENTER}
        zoom={MAP_CONFIG.DEFAULT_ZOOM}
        style={{ width: '100%', height: '100%' }}
        zoomControl={false}
      >
        {/* Tile Layer - Bản đồ nền */}
        <TileLayer
          attribution={MAP_CONFIG.TILE_LAYER.attribution}
          url={MAP_CONFIG.TILE_LAYER.url}
        />

        {/* Zoom Control - Góc dưới phải */}
        <ZoomControl position="bottomright" />

        {/* Component xử lý resize */}
        <MapReSizer />

        {/* Stops Layer */}
        {layers.includes('stops') && (
          <StopsLayer
            visible={true}
            selectedStopId={selectedStopId}
            onStopClick={handleStopClick}
          />
        )}

        {/* Bus Layer - Real-time bus positions */}
        {layers.includes('buses') && (
          <BusLayer
            buses={buses?.buses || []}
            selectedBusId={selectedBusId}
            trackedBusId={trackedBusId}
            onBusClick={handleBusClick}
            visible={true}
          />
        )}

        {/* Selected Route Polyline - Always show when a route is selected */}
        {selectedRoute && (
          <RoutePolyline
            route={selectedRoute}
            color="#00C060"
            weight={5}
            opacity={0.9}
            onClick={onRouteClick}
          />
        )}

        {/* Map Controls - BÊN TRONG MapContainer */}
        <MapControlsWrapper selectedStop={selectedStopData} />
      </MapContainer>
    </Box>
  );
};

export default BusMap;