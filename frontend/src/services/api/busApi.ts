import type { IHttpClient } from '@/types/http';
import type { ApiResponse } from '@/services/api';
import type { IBusAdapter } from '@/services/adapters/busAdapter';
import type {
  Bus,
  BusDTO,
  BusLocationDetails,
  BusLocationDetailsDTO,
  NearestBus,
  NearestBusDTO,
  CreateBusPayload,
  UpdateBusPayload,
  UpdateBusStatusPayload,
  UpdateBusLocationPayload,
  AssignBusToRoutePayload,
} from '@/types/bus';

export interface IBusService {
  // Read operations
  getBusById(busId: number): Promise<Bus>;
  getBusByPlateNumber(plateNumber: string): Promise<Bus>;
  getAllActiveBuses(): Promise<Bus[]>;
  getAllBuses(includeInactive?: boolean): Promise<Bus[]>;
  getBusesByRoute(routeId: number): Promise<Bus[]>;
  findNearestBuses(
    latitude: number,
    longitude: number,
    routeId?: number,
    limit?: number
  ): Promise<NearestBus[]>;
  getActiveBusCount(): Promise<number>;
  checkBusOnRoute(busId: number, toleranceMeters?: number): Promise<boolean>;
  getBusLocationDetails(busId: number): Promise<BusLocationDetails>;

  // Write operations (Admin or Driver)
  createBus(payload: CreateBusPayload): Promise<Bus>;
  updateBus(busId: number, payload: UpdateBusPayload): Promise<Bus>;
  updateBusStatus(busId: number, payload: UpdateBusStatusPayload): Promise<void>;
  updateBusLocation(
    busId: number,
    payload: UpdateBusLocationPayload
  ): Promise<void>;
  assignBusToRoute(
    busId: number,
    payload: AssignBusToRoutePayload
  ): Promise<void>;
  deleteBus(busId: number): Promise<void>;
}

export class BusService implements IBusService {
  constructor(
    private http: IHttpClient,
    private adapter: IBusAdapter
  ) {}

  async getBusById(busId: number): Promise<Bus> {
    const response = await this.http.get<ApiResponse<BusDTO>>(
      `/buses/${busId}`
    );
    return this.adapter.toBus(response.data);
  }

  async getBusByPlateNumber(plateNumber: string): Promise<Bus> {
    const response = await this.http.get<ApiResponse<BusDTO>>(
      `/buses/plate/${plateNumber}`
    );
    return this.adapter.toBus(response.data);
  }

  async getAllActiveBuses(): Promise<Bus[]> {
    const response = await this.http.get<ApiResponse<BusDTO[]>>('/buses/active');
    return response.data.map((dto) => this.adapter.toBus(dto));
  }

  async getAllBuses(includeInactive: boolean = false): Promise<Bus[]> {
    const response = await this.http.get<ApiResponse<BusDTO[]>>('/buses/', {
      params: { include_inactive: includeInactive },
    });
    return response.data.map((dto) => this.adapter.toBus(dto));
  }

  async getBusesByRoute(routeId: number): Promise<Bus[]> {
    const response = await this.http.get<ApiResponse<BusDTO[]>>(
      `/buses/route/${routeId}`
    );
    return response.data.map((dto) => this.adapter.toBus(dto));
  }

  async findNearestBuses(
    latitude: number,
    longitude: number,
    routeId?: number,
    limit: number = 5
  ): Promise<NearestBus[]> {
    const response = await this.http.get<ApiResponse<NearestBusDTO[]>>(
      '/buses/nearest',
      {
        params: {
          latitude,
          longitude,
          ...(routeId && { route_id: routeId }),
          limit,
        },
      }
    );
    return response.data.map((dto) => this.adapter.toNearestBus(dto));
  }

  async getActiveBusCount(): Promise<number> {
    const response = await this.http.get<ApiResponse<{ count: number }>>(
      '/buses/count/active'
    );
    return response.data.count;
  }

  async checkBusOnRoute(
    busId: number,
    toleranceMeters: number = 100
  ): Promise<boolean> {
    const response = await this.http.get<ApiResponse<{ is_on_route: boolean }>>(
      `/buses/${busId}/on-route`,
      {
        params: { tolerance_meters: toleranceMeters },
      }
    );
    return response.data.is_on_route;
  }

  async getBusLocationDetails(busId: number): Promise<BusLocationDetails> {
    const response = await this.http.get<ApiResponse<BusLocationDetailsDTO>>(
      `/buses/${busId}/location-details`
    );
    return this.adapter.toBusLocationDetails(response.data);
  }

  async createBus(payload: CreateBusPayload): Promise<Bus> {
    const response = await this.http.post<ApiResponse<BusDTO>>(
      '/buses/',
      payload
    );
    return this.adapter.toBus(response.data);
  }

  async updateBus(busId: number, payload: UpdateBusPayload): Promise<Bus> {
    const response = await this.http.put<ApiResponse<BusDTO>>(
      `/buses/${busId}`,
      payload
    );
    return this.adapter.toBus(response.data);
  }

  async updateBusStatus(
    busId: number,
    payload: UpdateBusStatusPayload
  ): Promise<void> {
    await this.http.put(`/buses/${busId}/status`, payload);
  }

  async updateBusLocation(
    busId: number,
    payload: UpdateBusLocationPayload
  ): Promise<void> {
    await this.http.put(`/buses/${busId}/location`, payload);
  }

  async assignBusToRoute(
    busId: number,
    payload: AssignBusToRoutePayload
  ): Promise<void> {
    await this.http.put(`/buses/${busId}/assign-route`, payload);
  }

  async deleteBus(busId: number): Promise<void> {
    await this.http.delete(`/buses/${busId}`);
  }
}
