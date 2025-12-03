import React from 'react';
import { useMap } from 'react-leaflet';
import { Paper, IconButton, Tooltip, Divider } from '@mui/material';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import CenterFocusStrongIcon from '@mui/icons-material/CenterFocusStrong';
import type { Stop } from '@/types/stop';
import type { Route } from '@/types/route';

interface MapControlsProps {
  onLocateMe?: () => void;
  selectedStop?: Stop | null;
  selectedRoute?: Route | null;
}

const MapControls: React.FC<MapControlsProps> = ({
  onLocateMe,
  selectedStop,
// selectedRoute,
}) => {
  const map = useMap();

  const handleZoomIn = () => {
    map.zoomIn();
  };

  const handleZoomOut = () => {
    map.zoomOut();
  };

  const handleLocateMe = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          map.setView([latitude, longitude], 16, { animate: true });
          onLocateMe?.();
        },
        (error) => {
          console.error('Geolocation error:', error);
          alert('Không thể lấy vị trí của bạn. Vui lòng bật GPS.');
        }
      );
    } else {
      alert('Trình duyệt không hỗ trợ định vị.');
    }
  };

  const handleFocusStop = () => {
    if (selectedStop) {
      map.setView(
        [selectedStop.latitude, selectedStop.longitude],
        17,
        { animate: true }
      );
    }
  };

  // const handleFitRoute = () => {
  //   if (selectedRoute) {
  //     // TODO: Implement fit route bounds
  //     console.log('Fit route bounds:', selectedRoute);
  //   }
  // };

  return (
    <Paper
      elevation={3}
      className="leaflet-control" // Thêm class để Leaflet nhận biết
      sx={{
        position: 'absolute',
        left: 16,
        bottom: 100,
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
        overflow: 'hidden',
      }}
    >
      {/* Zoom In */}
      <Tooltip title="Phóng to" placement="right">
        <IconButton onClick={handleZoomIn} sx={{ borderRadius: 0 }}>
          <AddIcon />
        </IconButton>
      </Tooltip>

      <Divider />

      {/* Zoom Out */}
      <Tooltip title="Thu nhỏ" placement="right">
        <IconButton onClick={handleZoomOut} sx={{ borderRadius: 0 }}>
          <RemoveIcon />
        </IconButton>
      </Tooltip>

      <Divider />

      {/* Locate Me */}
      <Tooltip title="Vị trí của tôi" placement="right">
        <IconButton onClick={handleLocateMe} sx={{ borderRadius: 0 }}>
          <MyLocationIcon />
        </IconButton>
      </Tooltip>

      {/* Focus on selected stop */}
      {selectedStop && (
        <>
          <Divider />
          <Tooltip title="Zoom đến điểm dừng" placement="right">
            <IconButton onClick={handleFocusStop} sx={{ borderRadius: 0 }}>
              <CenterFocusStrongIcon color="primary" />
            </IconButton>
          </Tooltip>
        </>
      )}
    </Paper>
  );
};

export default MapControls;