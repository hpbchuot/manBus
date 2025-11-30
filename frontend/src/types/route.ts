// Domain Models
export interface Route {
  id: number;
  name: string;
  currentSegment?: number;
  updatedAt?: string;
  stopCount?: number;
  lengthMeters?: number;
}

export interface RouteDetails extends Route {
  coordinates?: Coordinate[];
  stops?: RouteStop[];
}

export interface RouteStop {
  stopId: number;
  name: string;
  sequence: number;
  location: Location;
}

export interface Coordinate {
  latitude: number;
  longitude: number;
}

export interface Location {
  latitude: number;
  longitude: number;
}

export interface RouteGeoJSON {
  type: string;
  coordinates: [number, number][];
}

// DTOs (API Response/Request)
export interface RouteDTO {
  id: number;
  name: string;
  current_segment?: number;
  updated_at?: string;
  stop_count?: number;
  length_meters?: number;
}

export interface RouteStopDTO {
  stop_id: number;
  name: string;
  sequence: number;
  location: {
    latitude: number;
    longitude: number;
  };
}

export interface RouteGeoJSONDTO {
  type: string;
  coordinates: [number, number][];
}

export interface RouteNearDTO {
  id: number;
  name: string;
  distance_meters: number;
}

// Journey/Destination types
export interface BusRouteJourney {
  busId: number;
  plateNumber: string;
  busName: string;
  routeId: number;
  routeName: string;
  busDistanceFromOrigin: number;
  originDistanceFromRoute: number;
  destDistanceFromRoute: number;
  busLocation: Location;
}

export interface BusRouteJourneyDTO {
  bus_id: number;
  plate_number: string;
  bus_name: string;
  route_id: number;
  route_name: string;
  bus_distance_from_origin: number;
  origin_distance_from_route: number;
  dest_distance_from_route: number;
  bus_lat: number;
  bus_lon: number;
}

// Payloads
export interface CreateRoutePayload {
  name: string;
  coordinates: [number, number][];
}

export interface UpdateRoutePayload {
  name?: string;
  coordinates?: [number, number][];
}

export interface UpdateRouteGeometryPayload {
  coordinates: [number, number][];
}

export interface AddStopToRoutePayload {
  sequence: number;
}

export interface ReorderStopsPayload {
  stop_sequences: Array<{
    stop_id: number;
    sequence: number;
  }>;
}
