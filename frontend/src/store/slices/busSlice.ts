import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { Bus } from '@/types/bus';

/**
 * Bus Slice - Manages global bus state
 *
 * This slice handles:
 * - Selected bus for viewing details
 * - Tracking buses (following a bus on the map)
 * - Real-time bus updates
 */

interface BusState {
  selectedBus: Bus | null;
  trackedBusId: number | null; // Bus being followed on map
  realtimeUpdates: Record<number, Bus>; // Real-time bus positions
  filters: {
    routeId: number | null;
    status: 'active' | 'all';
  };
}

const initialState: BusState = {
  selectedBus: null,
  trackedBusId: null,
  realtimeUpdates: {},
  filters: {
    routeId: null,
    status: 'active',
  },
};

const busSlice = createSlice({
  name: 'bus',
  initialState,
  reducers: {
    // Select a bus to view details
    selectBus: (state, action: PayloadAction<Bus | null>) => {
      state.selectedBus = action.payload;
    },

    // Track a bus (follow on map)
    trackBus: (state, action: PayloadAction<number | null>) => {
      state.trackedBusId = action.payload;
    },

    // Update real-time bus location
    updateBusLocation: (state, action: PayloadAction<Bus>) => {
      state.realtimeUpdates[action.payload.busId] = action.payload;

      // Update selected bus if it's the same
      if (state.selectedBus?.busId === action.payload.busId) {
        state.selectedBus = action.payload;
      }
    },

    // Batch update multiple bus locations
    updateMultipleBusLocations: (state, action: PayloadAction<Bus[]>) => {
      action.payload.forEach((bus) => {
        state.realtimeUpdates[bus.busId] = bus;

        if (state.selectedBus?.busId === bus.busId) {
          state.selectedBus = bus;
        }
      });
    },

    // Clear real-time updates
    clearRealtimeUpdates: (state) => {
      state.realtimeUpdates = {};
    },

    // Set filters
    setRouteFilter: (state, action: PayloadAction<number | null>) => {
      state.filters.routeId = action.payload;
    },

    setStatusFilter: (state, action: PayloadAction<'active' | 'all'>) => {
      state.filters.status = action.payload;
    },

    // Reset bus state
    resetBusState: (state) => {
      state.selectedBus = null;
      state.trackedBusId = null;
      state.filters = initialState.filters;
    },
  },
});

export const {
  selectBus,
  trackBus,
  updateBusLocation,
  updateMultipleBusLocations,
  clearRealtimeUpdates,
  setRouteFilter,
  setStatusFilter,
  resetBusState,
} = busSlice.actions;

export default busSlice.reducer;
