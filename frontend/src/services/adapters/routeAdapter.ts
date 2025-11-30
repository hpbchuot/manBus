import type {
  Route,
  RouteStop,
  RouteDTO,
  RouteStopDTO,
  RouteGeoJSON,
  RouteGeoJSONDTO,
  BusRouteJourney,
  BusRouteJourneyDTO,
} from '@/types/route';
import { parseWKBPoint } from '@/utils/wkbParser';

export interface IRouteAdapter {
  toRoute(dto: RouteDTO): Route;
  toRouteStop(dto: RouteStopDTO): RouteStop;
  toRouteGeoJSON(dto: RouteGeoJSONDTO): RouteGeoJSON;
  toBusRouteJourney(dto: BusRouteJourneyDTO): BusRouteJourney;
}

export class RouteAdapter implements IRouteAdapter {
  toRoute(dto: RouteDTO): Route {
    return {
      id: dto.id,
      name: dto.name,
      currentSegment: dto.current_segment,
      updatedAt: dto.updated_at,
      stopCount: dto.stop_count,
      lengthMeters: dto.length_meters,
    };
  }

  toRouteStop(dto: RouteStopDTO): RouteStop {
    return {
      stopId: dto.stop_id,
      name: dto.name,
      sequence: dto.sequence,
      location: parseWKBPoint(dto.location),
    };
  }

  toRouteGeoJSON(dto: RouteGeoJSONDTO): RouteGeoJSON {
    return {
      type: dto.type,
      coordinates: dto.coordinates,
    };
  }

  toBusRouteJourney(dto: BusRouteJourneyDTO): BusRouteJourney {
    return {
      busId: dto.bus_id,
      plateNumber: dto.plate_number,
      busName: dto.bus_name,
      routeId: dto.route_id,
      routeName: dto.route_name,
      busDistanceFromOrigin: dto.bus_distance_from_origin,
      originDistanceFromRoute: dto.origin_distance_from_route,
      destDistanceFromRoute: dto.dest_distance_from_route,
      busLocation: {
        latitude: dto.bus_lat,
        longitude: dto.bus_lon,
      },
    };
  }
}