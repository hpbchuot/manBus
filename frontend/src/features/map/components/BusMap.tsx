import React, { useEffect } from 'react';
import { MapContainer, TileLayer, ZoomControl, useMap } from 'react-leaflet';
import { Box, useTheme } from '@mui/material';
import { MAP_CONFIG } from '../../../config/mapConfig';
import L from 'leaflet';

// Fix lỗi icon mặc định của Leaflet khi dùng với Webpack/Rsbuild
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

// --- Sub-component: Xử lý Resize ---
// Component này không render gì cả, chỉ lắng nghe thay đổi kích thước để báo cho Map vẽ lại
const MapReSizer = () => {
  const map = useMap();
  
  useEffect(() => {
    // ResizeObserver giúp theo dõi thay đổi kích thước của thẻ chứa Map
    const resizeObserver = new ResizeObserver(() => {
      // Gọi invalidateSize để Leaflet tính toán lại khung nhìn
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

// --- Main Component ---
const BusMap: React.FC = () => {
  const theme = useTheme();

  return (
    <Box sx={{ width: '100%', height: '100%', position: 'relative' }}>
      <MapContainer
        center={MAP_CONFIG.DEFAULT_CENTER}
        zoom={MAP_CONFIG.DEFAULT_ZOOM}
        style={{ width: '100%', height: '100%' }}
        zoomControl={false} // Tắt zoom mặc định để tự đặt vị trí
      >
        {/* Layer bản đồ Sáng/Sạch theo Design */}
        <TileLayer
          attribution={MAP_CONFIG.TILE_LAYER.attribution}
          url={MAP_CONFIG.TILE_LAYER.url}
        />

        {/* Đưa nút Zoom xuống góc dưới phải cho thoáng */}
        <ZoomControl position="bottomright" />

        {/* Component xử lý logic resize khi đóng mở sidebar */}
        <MapReSizer />
      </MapContainer>
    </Box>
  );
};

export default BusMap;