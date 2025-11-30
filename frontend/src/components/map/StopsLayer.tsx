import React, { useState, useEffect } from 'react';
import { useMap } from 'react-leaflet';
import StopMarker from './StopMarker';
import type { Stop } from '@/types/stop';
import { StopService } from '@/services/api/stopApi';
import { StopAdapter } from '@/services/adapters/stopAdapter';
import api from '@/services/api';
import { toast } from 'react-toastify';

interface StopsLayerProps {
  visible?: boolean;
  selectedStopId?: number | null;
  onStopClick?: (stop: Stop) => void;
}

const StopsLayer: React.FC<StopsLayerProps> = ({
  visible = true,
  selectedStopId = null,
  onStopClick,
}) => {
  const map = useMap();
  const [stops, setStops] = useState<Stop[]>([]);
  // const [loading, setLoading] = useState(false);
  // const [error, setError] = useState<string | null>(null);

  // Initialize services
  const stopAdapter = new StopAdapter();
  const stopService = new StopService(api, stopAdapter);

  // Load stops khi component mount
  useEffect(() => {
    loadStops();
  }, []);

  const loadStops = async () => {
    // setLoading(true);
    // setError(null);
    try {
      const data = await stopService.getAllStops();
      setStops(data);
    } catch (err: any) {
      const message = err.response?.data?.message || 'Không thể tải danh sách điểm dừng';
      // setError(message);
      toast.error(message);
    } finally {
      // setLoading(false);
    }
  };

  // Load stops gần vị trí hiện tại của map khi zoom/pan
  useEffect(() => {
    if (!visible) return;

    const handleMoveEnd = async () => {
      const center = map.getCenter();
      const zoom = map.getZoom();

      // Chỉ load stops khi zoom đủ gần (level 13+)
      if (zoom < 13) return;

      try {
        const nearbyStops = await stopService.findNearestStops(
          center.lat,
          center.lng,
          5000, // 5km radius
          50 // Limit 50 stops
        );
        
        // Merge với stops hiện có (không duplicate)
        setStops((prevStops) => {
          const existingIds = new Set(prevStops.map(s => s.id));
          const newStops = nearbyStops.filter(s => !existingIds.has(s.id));
          return [...prevStops, ...newStops];
        });
      } catch (err) {
        console.error('Error loading nearby stops:', err);
      }
    };

    map.on('moveend', handleMoveEnd);
    return () => {
      map.off('moveend', handleMoveEnd);
    };
  }, [map, visible]);

  if (!visible) return null;

  return (
    <>
      {stops.map((stop) => (
        <StopMarker
          key={stop.id}
          stop={stop}
          isSelected={stop.id === selectedStopId}
          onClick={onStopClick}
        />
      ))}
    </>
  );
};

export default StopsLayer;