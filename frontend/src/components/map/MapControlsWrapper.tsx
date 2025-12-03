import React, { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import { createPortal } from 'react-dom';
import { Paper, IconButton, Tooltip, Divider } from '@mui/material';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import CenterFocusStrongIcon from '@mui/icons-material/CenterFocusStrong';
import type { Stop } from '@/types/stop';

interface MapControlsWrapperProps {
  selectedStop?: Stop | null;
}

const MapControlsWrapper: React.FC<MapControlsWrapperProps> = ({ selectedStop }) => {
  const map = useMap();
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Tạo container div cho controls
    const container = document.createElement('div');
    container.style.position = 'absolute';
    container.style.left = '16px';
    container.style.bottom = '100px';
    container.style.zIndex = '1000';
    
    // Thêm vào map container
    map.getContainer().appendChild(container);
    containerRef.current = container;

    return () => {
      // Cleanup khi unmount
      if (containerRef.current && map.getContainer().contains(containerRef.current)) {
        map.getContainer().removeChild(containerRef.current);
      }
    };
  }, [map]);

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

  const controls = (
    <Paper
      elevation={3}
      sx={{
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

  // Render controls vào container đã tạo
  return containerRef.current ? createPortal(controls, containerRef.current) : null;
};

export default MapControlsWrapper;