import type { IHttpClient } from '@/types/http';
import type { ApiResponse } from '@/services/api';
import type { IRouteAdapter } from '@/services/adapters/routeAdapter';
import type {
  Route,
  RouteStop,
  RouteGeoJSON,
  RouteDTO,
  RouteStopDTO,
  RouteGeoJSONDTO,
  BusRouteJourney,
  BusRouteJourneyDTO,
  CreateRoutePayload,
  UpdateRoutePayload,
  UpdateRouteGeometryPayload,
  AddStopToRoutePayload,
  ReorderStopsPayload,
} from '@/types/route';

export interface IRouteService {
  // Read operations
  getRouteById(routeId: number): Promise<Route>;
  getRouteByName(routeName: string): Promise<Route>;
  getAllRoutes(cursor?: number, limit?: number): Promise<{ routes: Route[]; next_cursor: number | null; has_next: boolean }>;
  getRouteStops(routeId: number): Promise<RouteStop[]>;
  getRouteLength(routeId: number): Promise<number>;
  getRouteGeoJSON(routeId: number): Promise<RouteGeoJSON>;
  findRoutesNearLocation(
    latitude: number,
    longitude: number,
    radiusMeters?: number
  ): Promise<Route[]>;
  checkPointOnRoute(
    routeId: number,
    latitude: number,
    longitude: number,
    toleranceMeters?: number
  ): Promise<boolean>;
  findBusesToDestination(
    originLatitude: number,
    originLongitude: number,
    destinationLatitude: number,
    destinationLongitude: number
  ): Promise<BusRouteJourney[]>;

  // Write operations (Admin only)
  createRoute(payload: CreateRoutePayload): Promise<Route>;
  updateRoute(routeId: number, payload: UpdateRoutePayload): Promise<Route>;
  updateRouteGeometry(
    routeId: number,
    payload: UpdateRouteGeometryPayload
  ): Promise<void>;
  addStopToRoute(
    routeId: number,
    stopId: number,
    payload: AddStopToRoutePayload
  ): Promise<void>;
  removeStopFromRoute(routeId: number, stopId: number): Promise<void>;
  reorderRouteStops(routeId: number, payload: ReorderStopsPayload): Promise<void>;
  deleteRoute(routeId: number): Promise<void>;
}

export class RouteService implements IRouteService {
  constructor(
    private http: IHttpClient,
    private adapter: IRouteAdapter
  ) {}

  async getRouteById(routeId: number): Promise<Route> {
    const response = await this.http.get<ApiResponse<RouteDTO>>(
      `/routes/${routeId}`
    );
    return this.adapter.toRoute(response.data);
  }

  async getRouteByName(routeName: string): Promise<Route> {
    const response = await this.http.get<ApiResponse<RouteDTO>>(
      `/routes/name/${routeName}`
    );
    return this.adapter.toRoute(response.data);
  }

  async getAllRoutes(cursor?: number, limit: number = 10): Promise<{ routes: Route[]; next_cursor: number | null; has_next: boolean }> {
    const response = await this.http.get<ApiResponse<{
      routes: RouteDTO[];
      next_cursor: number | null;
      has_next: boolean;
    }>>('/routes/', {
      params: {
        cursor,
        limit,
      },
    });

    return {
      routes: response.data.routes.map((dto) => this.adapter.toRoute(dto)),
      next_cursor: response.data.next_cursor,
      has_next: response.data.has_next,
    };
  }

  async getRouteStops(routeId: number): Promise<RouteStop[]> {
    const response = await this.http.get<ApiResponse<RouteStopDTO[]>>(
      `/routes/${routeId}/stops`
    );
    return response.data.map((dto) => this.adapter.toRouteStop(dto));
  }

  async getRouteLength(routeId: number): Promise<number> {
    const response = await this.http.get<ApiResponse<{ length: number }>>(
      `/routes/${routeId}/length`
    );
    return response.data.length;
  }

  async getRouteGeoJSON(routeId: number): Promise<RouteGeoJSON> {
    const response = await this.http.get<ApiResponse<RouteGeoJSONDTO>>(
      `/routes/${routeId}/geojson`
    );
    return this.adapter.toRouteGeoJSON(response.data);
  }

  async findRoutesNearLocation(
    latitude: number,
    longitude: number,
    radiusMeters: number = 500
  ): Promise<Route[]> {
    const response = await this.http.get<ApiResponse<RouteDTO[]>>(
      `/routes/near`,
      {
        params: { latitude, longitude, radius_meters: radiusMeters },
      }
    );
    return response.data.map((dto) => this.adapter.toRoute(dto));
  }

  async checkPointOnRoute(
    routeId: number,
    latitude: number,
    longitude: number,
    toleranceMeters: number = 100
  ): Promise<boolean> {
    const response = await this.http.get<ApiResponse<{ is_on_route: boolean }>>(
      `/routes/${routeId}/check-point`,
      {
        params: { latitude, longitude, tolerance_meters: toleranceMeters },
      }
    );
    return response.data.is_on_route;
  }

  async findBusesToDestination(
    originLatitude: number,
    originLongitude: number,
    destinationLatitude: number,
    destinationLongitude: number
  ): Promise<BusRouteJourney[]> {
    const response = await this.http.get<ApiResponse<BusRouteJourneyDTO[]>>(
      '/routes/journey',
      {
        params: {
          origin_latitude: originLatitude,
          origin_longitude: originLongitude,
          destination_latitude: destinationLatitude,
          destination_longitude: destinationLongitude,
        },
      }
    );
    return response.data.map((dto) => this.adapter.toBusRouteJourney(dto));
  }

  async createRoute(payload: CreateRoutePayload): Promise<Route> {
    const response = await this.http.post<ApiResponse<RouteDTO>>(
      '/routes/',
      payload
    );
    return this.adapter.toRoute(response.data);
  }

  async updateRoute(
    routeId: number,
    payload: UpdateRoutePayload
  ): Promise<Route> {
    const response = await this.http.put<ApiResponse<RouteDTO>>(
      `/routes/${routeId}`,
      payload
    );
    return this.adapter.toRoute(response.data);
  }

  async updateRouteGeometry(
    routeId: number,
    payload: UpdateRouteGeometryPayload
  ): Promise<void> {
    await this.http.put(`/routes/${routeId}/geometry`, payload);
  }

  async addStopToRoute(
    routeId: number,
    stopId: number,
    payload: AddStopToRoutePayload
  ): Promise<void> {
    await this.http.post(`/routes/${routeId}/stops/${stopId}`, payload);
  }

  async removeStopFromRoute(routeId: number, stopId: number): Promise<void> {
    await this.http.delete(`/routes/${routeId}/stops/${stopId}`);
  }

  async reorderRouteStops(
    routeId: number,
    payload: ReorderStopsPayload
  ): Promise<void> {
    await this.http.put(`/routes/${routeId}/stops/reorder`, payload);
  }

  async deleteRoute(routeId: number): Promise<void> {
    await this.http.delete(`/routes/${routeId}`);
  }
}
