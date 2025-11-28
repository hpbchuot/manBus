import type { Stop, StopDTO, NearestStop, NearestStopDTO } from '@/types/stop';
import { parseWKBPoint } from '@/utils/wkbParser';

export interface IStopAdapter {
  toStop(dto: StopDTO): Stop;
  toNearestStop(dto: NearestStopDTO): NearestStop;
}

export class StopAdapter implements IStopAdapter {
  toStop(dto: StopDTO): Stop {
    return {
      id: dto.id,
      name: dto.name,
      location: parseWKBPoint(dto.location),
    };
  }

  toNearestStop(dto: NearestStopDTO): NearestStop {
    return {
      id: dto.id,
      name: dto.name,
      distanceMeters: dto.distance_meters,
      location: parseWKBPoint(dto.location),
    };
  }
}