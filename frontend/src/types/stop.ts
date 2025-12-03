// Domain Models
export interface Stop {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
}

export interface Location {
  latitude: number;
  longitude: number;
}

export interface NearestStop extends Stop {
  distanceMeters: number;
}

// DTOs (API Response/Request)
export interface StopDTO {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
}

export interface NearestStopDTO {
  id: number;
  name: string;
  distance_meters: number;
  location: string | {
    latitude: number;
    longitude: number;
  };
}

// Payloads
export interface CreateStopPayload {
  name: string;
  latitude: number;
  longitude: number;
}

export interface UpdateStopPayload {
  name?: string;
}
