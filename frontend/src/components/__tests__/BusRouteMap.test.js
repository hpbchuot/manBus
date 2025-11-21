import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import BusRouteMap from "../BusRouteMap";

// Mock react-leaflet to lightweight components for testing
jest.mock("react-leaflet", () => {
  const React = require("react");
  return {
    MapContainer: ({ children }) => <div data-testid="map">{children}</div>,
    TileLayer: () => <div data-testid="tile" />,
    Marker: ({ children }) => <div data-testid="marker">{children}</div>,
    Popup: ({ children }) => <div data-testid="popup">{children}</div>,
    Polyline: () => <div data-testid="polyline" />,
    ZoomControl: () => <div data-testid="zoom" />,
  };
});

// Helper to build a fake route response
const makeRoute = (id) => ({
  name: `Bus ${id}`,
  start: { lat: 21 + id * 0.001, lng: 105.8 + id * 0.001 },
  end: { lat: 21.05 + id * 0.001, lng: 105.85 + id * 0.001 },
  path: [
    [21 + id * 0.001, 105.8 + id * 0.001],
    [21.025 + id * 0.001, 105.825 + id * 0.001],
    [21.05 + id * 0.001, 105.85 + id * 0.001],
  ],
});

describe("BusRouteMap", () => {
  beforeEach(() => {
    jest.resetAllMocks();
  });

  test("fetches and renders markers and polylines for routes", async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({ ok: true, json: async () => makeRoute(1) })
      .mockResolvedValueOnce({ ok: true, json: async () => makeRoute(3) });

    render(<BusRouteMap routeIds={[1, 3]} />);

    // loading overlay appears first
    expect(screen.getByTestId("bus-route-map")).toBeInTheDocument();

    await waitFor(() => {
      // 4 markers: start + end for two routes
      const markers = screen.getAllByTestId("marker");
      expect(markers.length).toBe(4);

      // 2 polylines: one per route
      const polylines = screen.getAllByTestId("polyline");
      expect(polylines.length).toBe(2);
    });
  });

  test("shows error alert when a fetch fails", async () => {
    global.fetch = jest.fn().mockResolvedValue({ ok: false, status: 500 });

    render(<BusRouteMap routeIds={[1, 3]} />);

    await waitFor(() => {
      expect(screen.getByTestId("error-alert")).toBeInTheDocument();
    });
  });
});
