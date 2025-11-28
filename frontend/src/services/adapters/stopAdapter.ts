import type { Stop, StopDTO, NearestStop, NearestStopDTO } from '@/types/stop';

export interface IStopAdapter {
  toStop(dto: StopDTO): Stop;
  toNearestStop(dto: NearestStopDTO): NearestStop;
}

export class StopAdapter implements IStopAdapter {
  toStop(dto: StopDTO): Stop {
    return {
      id: dto.id,
      name: dto.name,
      location: {
        latitude: dto.location.latitude,
        longitude: dto.location.longitude,
      },
    };
  }

  toNearestStop(dto: NearestStopDTO): NearestStop {
    return {
      id: dto.id,
      name: dto.name,
      distanceMeters: dto.distance_meters,
      location: {
        latitude: dto.location.latitude,
        longitude: dto.location.longitude,
      },
    };
  }
}
