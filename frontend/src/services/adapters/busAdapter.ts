import type {
  Bus,
  BusDTO,
  BusLocationDetails,
  BusLocationDetailsDTO,
  NearestBus,
  NearestBusDTO,
  BusStatus,
} from '@/types/bus';
import { parseWKBPoint } from '@/utils/wkbParser';

export interface IBusAdapter {
  toBus(dto: BusDTO): Bus;
  toBusLocationDetails(dto: BusLocationDetailsDTO): BusLocationDetails;
  toNearestBus(dto: NearestBusDTO): NearestBus;
}

export class BusAdapter implements IBusAdapter {
  toBus(dto: BusDTO): Bus {
    return {
      busId: dto.bus_id,
      plateNumber: dto.plate_number,
      name: dto.name,
      model: dto.model,
      status: dto.status as BusStatus,
      routeId: dto.route_id,
      routeName: dto.route_name,
      currentLocation: dto.current_location
        ? parseWKBPoint(dto.current_location)
        : undefined,
      lastUpdated: dto.last_updated,
    };
  }

  toBusLocationDetails(dto: BusLocationDetailsDTO): BusLocationDetails {
    return {
      busId: dto.bus_id,
      currentLocation: parseWKBPoint(dto.current_location),
      distanceFromRoute: dto.distance_from_route,
      lastUpdated: dto.last_updated,
    };
  }

  toNearestBus(dto: NearestBusDTO): NearestBus {
    return {
      busId: dto.bus_id,
      plateNumber: dto.plate_number,
      distanceMeters: dto.distance_meters,
      currentLocation: parseWKBPoint(dto.current_location),
    };
  }
}