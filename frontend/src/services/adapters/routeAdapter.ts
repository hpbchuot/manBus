import type {
  Route,
  RouteStop,
  RouteDTO,
  RouteStopDTO,
  RouteGeoJSON,
  RouteGeoJSONDTO,
} from '@/types/route';

export interface IRouteAdapter {
  toRoute(dto: RouteDTO): Route;
  toRouteStop(dto: RouteStopDTO): RouteStop;
  toRouteGeoJSON(dto: RouteGeoJSONDTO): RouteGeoJSON;
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
      location: {
        latitude: dto.location.latitude,
        longitude: dto.location.longitude,
      },
    };
  }

  toRouteGeoJSON(dto: RouteGeoJSONDTO): RouteGeoJSON {
    return {
      type: dto.type,
      coordinates: dto.coordinates,
    };
  }
}
