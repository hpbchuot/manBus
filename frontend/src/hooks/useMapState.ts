import { useState, useCallback } from 'react';
import type { Stop } from '@/types/stop';
import type { Route } from '@/types/route';
import type { Bus } from '@/types/bus';

interface MapState {
  center: [number, number];
  zoom: number;
  selectedStop: Stop | null;
  selectedRoute: Route | null;
  selectedBus: Bus | null;
  visibleLayers: string[];
}

const DEFAULT_MAP_STATE: MapState = {
  center: [21.0285, 105.8542], // Hà Nội
  zoom: 14,
  selectedStop: null,
  selectedRoute: null,
  selectedBus: null,
  visibleLayers: ['stops', 'routes'],
};

export const useMapState = () => {
  const [mapState, setMapState] = useState<MapState>(DEFAULT_MAP_STATE);

  // Select Stop
  const selectStop = useCallback((stop: Stop | null) => {
    setMapState((prev) => ({
      ...prev,
      selectedStop: stop,
      center: stop ? [stop.location.latitude, stop.location.longitude] : prev.center,
      zoom: stop ? 17 : prev.zoom,
    }));
  }, []);

  // Select Route
  const selectRoute = useCallback((route: Route | null) => {
    setMapState((prev) => ({
      ...prev,
      selectedRoute: route,
    }));
  }, []);

  // Select Bus
  const selectBus = useCallback((bus: Bus | null) => {
    setMapState((prev) => ({
      ...prev,
      selectedBus: bus,
      center: bus?.currentLocation
        ? [bus.currentLocation.latitude, bus.currentLocation.longitude]
        : prev.center,
      zoom: bus ? 16 : prev.zoom,
    }));
  }, []);

  // Toggle Layer Visibility
  const toggleLayer = useCallback((layer: string) => {
    setMapState((prev) => {
      const isVisible = prev.visibleLayers.includes(layer);
      return {
        ...prev,
        visibleLayers: isVisible
          ? prev.visibleLayers.filter((l) => l !== layer)
          : [...prev.visibleLayers, layer],
      };
    });
  }, []);

  // Set Layers
  const setLayers = useCallback((layers: string[]) => {
    setMapState((prev) => ({
      ...prev,
      visibleLayers: layers,
    }));
  }, []);

  // Set Map View
  const setMapView = useCallback((center: [number, number], zoom: number) => {
    setMapState((prev) => ({
      ...prev,
      center,
      zoom,
    }));
  }, []);

  // Reset Map State
  const resetMapState = useCallback(() => {
    setMapState(DEFAULT_MAP_STATE);
  }, []);

  return {
    mapState,
    selectStop,
    selectRoute,
    selectBus,
    toggleLayer,
    setLayers,
    setMapView,
    resetMapState,
  };
};