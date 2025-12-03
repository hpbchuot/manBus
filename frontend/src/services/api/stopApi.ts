import type { IHttpClient } from '@/types/http';
import type { ApiResponse } from '@/services/api';

import type {
  Stop,
  StopDTO,
  NearestStop,
  CreateStopPayload,
  UpdateStopPayload,
} from '@/types/stop';

export interface IStopService {
  // Read operations
  getStopById(stopId: number): Promise<Stop>;
  getAllStops(cursor?: number, limit?: number): Promise<{ stops: Stop[]; next_cursor: number | null; has_next: boolean }>;
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
    private http: IHttpClient
  ) {}

  async getStopById(stopId: number): Promise<Stop> {
    const response = await this.http.get<ApiResponse<StopDTO>>(
      `/stops/${stopId}`
    );
    return response.data;
  }

  async getAllStops(cursor?: number, limit: number = 100): Promise<{ stops: Stop[]; next_cursor: number | null; has_next: boolean }> {
    const response = await this.http.get<ApiResponse<{
      stops: Stop[];
      next_cursor: number | null;
      has_next: boolean;
    }>>('/stops', {
      params: {
        cursor,
        limit: limit,
      },
    });

    return {
      stops: response.data.stops,
      next_cursor: response.data.next_cursor,
      has_next: response.data.has_next,
    };
  }

  async findNearestStops(
    latitude: number,
    longitude: number,
    radiusMeters: number = 1000,
    limit: number = 10
  ): Promise<NearestStop[]> {
    const response = await this.http.get<ApiResponse<NearestStop[]>>(
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
    return response.data;
  }

  async createStop(payload: CreateStopPayload): Promise<Stop> {
    const response = await this.http.post<ApiResponse<StopDTO>>(
      '/stops/',
      payload
    );
    return response.data;
  }

  async updateStop(stopId: number, payload: UpdateStopPayload): Promise<Stop> {
    const response = await this.http.put<ApiResponse<StopDTO>>(
      `/stops/${stopId}`,
      payload
    );
    return response.data;
  }

  async deleteStop(stopId: number): Promise<void> {
    await this.http.delete(`/stops/${stopId}`);
  }
}
