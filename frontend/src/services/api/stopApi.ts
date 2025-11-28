import type { IHttpClient } from '@/types/http';
import type { ApiResponse } from '@/services/api';
import type { IStopAdapter } from '@/services/adapters/stopAdapter';
import type {
  Stop,
  StopDTO,
  NearestStop,
  NearestStopDTO,
  CreateStopPayload,
  UpdateStopPayload,
} from '@/types/stop';

export interface IStopService {
  // Read operations
  getStopById(stopId: number): Promise<Stop>;
  getAllStops(): Promise<Stop[]>;
  findNearestStops(
    latitude: number,
    longitude: number,
    radiusMeters?: number,
    limit?: number
  ): Promise<NearestStop[]>;

  // Write operations (Admin only)
  createStop(payload: CreateStopPayload): Promise<Stop>;
  updateStop(stopId: number, payload: UpdateStopPayload): Promise<Stop>;
  deleteStop(stopId: number): Promise<void>;
}

export class StopService implements IStopService {
  constructor(
    private http: IHttpClient,
    private adapter: IStopAdapter
  ) {}

  async getStopById(stopId: number): Promise<Stop> {
    const response = await this.http.get<ApiResponse<StopDTO>>(
      `/stops/${stopId}`
    );
    return this.adapter.toStop(response.data);
  }

  async getAllStops(): Promise<Stop[]> {
    const response = await this.http.get<ApiResponse<StopDTO[]>>('/stops/');
    return response.data.map((dto) => this.adapter.toStop(dto));
  }

  async findNearestStops(
    latitude: number,
    longitude: number,
    radiusMeters: number = 1000,
    limit: number = 10
  ): Promise<NearestStop[]> {
    const response = await this.http.get<ApiResponse<NearestStopDTO[]>>(
      '/stops/nearest',
      {
        params: {
          latitude,
          longitude,
          radius_meters: radiusMeters,
          limit,
        },
      }
    );
    return response.data.map((dto) => this.adapter.toNearestStop(dto));
  }

  async createStop(payload: CreateStopPayload): Promise<Stop> {
    const response = await this.http.post<ApiResponse<StopDTO>>(
      '/stops/',
      payload
    );
    return this.adapter.toStop(response.data);
  }

  async updateStop(stopId: number, payload: UpdateStopPayload): Promise<Stop> {
    const response = await this.http.put<ApiResponse<StopDTO>>(
      `/stops/${stopId}`,
      payload
    );
    return this.adapter.toStop(response.data);
  }

  async deleteStop(stopId: number): Promise<void> {
    await this.http.delete(`/stops/${stopId}`);
  }
}
