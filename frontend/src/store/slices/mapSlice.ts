import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { Stop } from '@/types/stop';
import type { Route } from '@/types/route';
import type { Bus } from '@/types/bus';

/**
 * Map Slice - Manages map state globally
 *
 * This slice handles:
 * - Map center and zoom level
 * - Selected entities (stop, route, bus)
 * - Visible layers
 * - Map view mode (journey planning, bus tracking, etc.)
 */

export type MapViewMode = 'default' | 'journey' | 'tracking' | 'route-view';

interface MapState {
  center: [number, number];
  zoom: number;
  viewMode: MapViewMode;
  selectedStop: Stop | null;
  selectedRoute: Route | null;
  selectedBus: Bus | null;
  visibleLayers: {
    stops: boolean;
    routes: boolean;
    buses: boolean;
    traffic: boolean;
  };
  journey: {
    origin: [number, number] | null;
    destination: [number, number] | null;
    showResults: boolean;
  };
}

const DEFAULT_CENTER: [number, number] = [21.0285, 105.8542]; // Hà Nội
const DEFAULT_ZOOM = 14;

const initialState: MapState = {
  center: DEFAULT_CENTER,
  zoom: DEFAULT_ZOOM,
  viewMode: 'default',
  selectedStop: null,
  selectedRoute: null,
  selectedBus: null,
  visibleLayers: {
    stops: true,
    routes: true,
    buses: true,
    traffic: false,
  },
  journey: {
    origin: null,
    destination: null,
    showResults: false,
  },
};

const mapSlice = createSlice({
  name: 'map',
  initialState,
  reducers: {
    // Set map view
    setMapView: (
      state,
      action: PayloadAction<{ center: [number, number]; zoom: number }>
    ) => {
      state.center = action.payload.center;
      state.zoom = action.payload.zoom;
    },

    // Set map center
    setMapCenter: (state, action: PayloadAction<[number, number]>) => {
      state.center = action.payload;
    },

    // Set map zoom
    setMapZoom: (state, action: PayloadAction<number>) => {
      state.zoom = action.payload;
    },

    // Set view mode
    setViewMode: (state, action: PayloadAction<MapViewMode>) => {
      state.viewMode = action.payload;
    },

    // Select stop
    selectStop: (state, action: PayloadAction<Stop | null>) => {
      state.selectedStop = action.payload;
      state.selectedRoute = null;
      state.selectedBus = null;

      if (action.payload) {
        state.center = [
          action.payload.latitude,
          action.payload.longitude,
        ];
        state.zoom = 17;
      }
    },

    // Select route
    selectRoute: (state, action: PayloadAction<Route | null>) => {
      state.selectedRoute = action.payload;
      state.selectedStop = null;
      state.selectedBus = null;
      state.viewMode = action.payload ? 'route-view' : 'default';
    },

    // Select bus
    selectBus: (state, action: PayloadAction<Bus | null>) => {
      state.selectedBus = action.payload;
      state.selectedStop = null;
      state.selectedRoute = null;

      if (action.payload?.currentLocation) {
        state.center = [
          action.payload.currentLocation.latitude,
          action.payload.currentLocation.longitude,
        ];
        state.zoom = 16;
      }
    },

    // Toggle layer visibility
    toggleLayer: (
      state,
      action: PayloadAction<keyof MapState['visibleLayers']>
    ) => {
      const layer = action.payload;
      state.visibleLayers[layer] = !state.visibleLayers[layer];
    },

    // Set layer visibility
    setLayerVisibility: (
      state,
      action: PayloadAction<{
        layer: keyof MapState['visibleLayers'];
        visible: boolean;
      }>
    ) => {
      state.visibleLayers[action.payload.layer] = action.payload.visible;
    },

    // Journey planning
    setJourneyOrigin: (state, action: PayloadAction<[number, number] | null>) => {
      state.journey.origin = action.payload;
      if (action.payload) {
        state.viewMode = 'journey';
      }
    },

    setJourneyDestination: (
      state,
      action: PayloadAction<[number, number] | null>
    ) => {
      state.journey.destination = action.payload;
    },

    setJourneyPoints: (
      state,
      action: PayloadAction<{
        origin: [number, number] | null;
        destination: [number, number] | null;
      }>
    ) => {
      state.journey.origin = action.payload.origin;
      state.journey.destination = action.payload.destination;
      if (action.payload.origin && action.payload.destination) {
        state.viewMode = 'journey';
        state.journey.showResults = true;
      }
    },

    clearJourney: (state) => {
      state.journey = {
        origin: null,
        destination: null,
        showResults: false,
      };
      state.viewMode = 'default';
    },

    // Reset map to default
    resetMapState: (state) => {
      state.center = DEFAULT_CENTER;
      state.zoom = DEFAULT_ZOOM;
      state.viewMode = 'default';
      state.selectedStop = null;
      state.selectedRoute = null;
      state.selectedBus = null;
      state.journey = initialState.journey;
    },

    // Clear selections
    clearSelections: (state) => {
      state.selectedStop = null;
      state.selectedRoute = null;
      state.selectedBus = null;
      state.viewMode = 'default';
    },
  },
});

export const {
  setMapView,
  setMapCenter,
  setMapZoom,
  setViewMode,
  selectStop,
  selectRoute,
  selectBus,
  toggleLayer,
  setLayerVisibility,
  setJourneyOrigin,
  setJourneyDestination,
  setJourneyPoints,
  clearJourney,
  resetMapState,
  clearSelections,
} = mapSlice.actions;

export default mapSlice.reducer;
