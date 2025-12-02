import { useQuery } from '@tanstack/react-query';
import api from '@/services/api';
import { RouteService } from '@/services/api/routeApi';
import { RouteAdapter } from '@/services/adapters/routeAdapter';

// Initialize service instances (singleton)
const routeAdapter = new RouteAdapter();
const routeService = new RouteService(api, routeAdapter);

/**
 * Hook to find buses/routes from origin to destination
 * This is useful for journey planning - finding which buses can take you from point A to B
 *
 * @param originLat - Origin latitude
 * @param originLng - Origin longitude
 * @param destLat - Destination latitude
 * @param destLng - Destination longitude
 * @param enabled - Whether to enable the query (default: true)
 *
 * @returns Query result with array of BusRouteJourney
 *
 * @example
 * const { data: journeys, isLoading } = useJourney(
 *   21.0285, 105.8542,  // origin (current location)
 *   21.0368, 105.8347   // destination (where you want to go)
 * );
 *
 * // journeys will contain:
 * // - Which buses are available
 * // - Their current distance from your origin
 * // - How far you need to walk to the route
 * // - How far you need to walk from the route to destination
 */
export const useJourney = (
  originLat: number,
  originLng: number,
  destLat: number,
  destLng: number,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: ['journey', originLat, originLng, destLat, destLng],
    queryFn: () =>
      routeService.findBusesToDestination(
        originLat,
        originLng,
        destLat,
        destLng
      ),
    enabled: enabled && !!originLat && !!originLng && !!destLat && !!destLng,
    staleTime: 1000 * 30, // Consider data fresh for 30 seconds (buses move frequently)
    refetchInterval: 1000 * 30, // Auto-refetch every 30 seconds for real-time updates
  });
};

/**
 * Hook variant that only fetches when explicitly called
 * Useful when you want manual control over when to search
 *
 * @example
 * const { data, refetch, isLoading } = useJourneyLazy(21.0285, 105.8542, 21.0368, 105.8347);
 *
 * // In your component
 * <Button onClick={() => refetch()}>Find Buses</Button>
 */
export const useJourneyLazy = (
  originLat: number,
  originLng: number,
  destLat: number,
  destLng: number
) => {
  return useJourney(originLat, originLng, destLat, destLng, false);
};
