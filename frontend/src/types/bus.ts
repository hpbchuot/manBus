// Domain Models
export interface Bus {
  busId: number;
  plateNumber: string;
  name: string;
  model?: string;
  status: BusStatus;
  routeId?: number;
  routeName?: string;
  currentLocation?: Location;
  lastUpdated?: string;
}

export interface Location {
  latitude: number;
  longitude: number;
}

export type BusStatus = 'Active' | 'Inactive' | 'Maintenance';

export interface BusLocationDetails {
  busId: number;
  currentLocation: Location;
  distanceFromRoute?: number;
  lastUpdated: string;
}

export interface NearestBus {
  busId: number;
  plateNumber: string;
  distanceMeters: number;
  currentLocation: Location;
}

// DTOs (API Response/Request)
export interface BusDTO {
  bus_id: number;
  plate_number: string;
  name: string;
  model?: string;
  status: string;
  route_id?: number;
  route_name?: string;
  current_location?: {
    latitude: number;
    longitude: number;
  };
  last_updated?: string;
}

export interface BusLocationDetailsDTO {
  bus_id: number;
  current_location: {
    latitude: number;
    longitude: number;
  };
  distance_from_route?: number;
  last_updated: string;
}

export interface NearestBusDTO {
  bus_id: number;
  plate_number: string;
  distance_meters: number;
  current_location: {
    latitude: number;
    longitude: number;
  };
}

// Payloads
export interface CreateBusPayload {
  plate_number: string;
  name: string;
  model?: string;
  status?: string;
  route_id?: number;
}

export interface UpdateBusPayload {
  name?: string;
  model?: string;
  status?: string;
}

export interface UpdateBusStatusPayload {
  status: string;
}

export interface UpdateBusLocationPayload {
  location: {
    latitude: number;
    longitude: number;
  };
}

export interface AssignBusToRoutePayload {
  route_id: number;
}
