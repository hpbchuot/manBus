import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query';
import api from '@/services/api';
import { StopService } from '@/services/api/stopApi';
import { RouteService } from '@/services/api/routeApi';
import { RouteAdapter } from '@/services/adapters/routeAdapter';
import { BusService } from '@/services/api/busApi';
import { BusAdapter } from '@/services/adapters/busAdapter';
// import type { NearestStop } from '@/types/stop';
import type { RouteGeoJSON } from '@/types/route';
import type { UpdateBusLocationPayload } from '@/types/bus';

// Khởi tạo Service (Singleton instances)
// Việc này đảm bảo chúng ta không tạo mới instance mỗi lần render
const stopService = new StopService(api);

const routeAdapter = new RouteAdapter();
const routeService = new RouteService(api, routeAdapter);

const busAdapter = new BusAdapter();
const busService = new BusService(api, busAdapter);

// --- HOOKS CHO STOPS ---

// 1. Lấy tất cả trạm (Có cache)
export const useAllStops = () => {
  return useQuery({
    queryKey: ['stops', 'all'],
    queryFn: async () => {
      const result = await stopService.getAllStops();
      return result.stops;
    },
    staleTime: 1000 * 60 * 5, // Data coi là mới trong 5 phút
  });
};

// 2. Tìm trạm gần nhất (Khi di chuyển map)
export const useNearestStops = (
  lat: number,
  lng: number,
  radius: number = 2000,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: ['stops', 'nearest', lat, lng, radius],
    queryFn: () => stopService.findNearestStops(lat, lng, radius, 50),
    enabled: enabled, // Chỉ chạy khi map zoom đủ gần
    placeholderData: keepPreviousData, // Giữ data cũ khi đang fetch data mới (tránh nhấp nháy)
  });
};

// --- HOOKS CHO ROUTES ---

// 3. Lấy hình dáng tuyến đường (GeoJSON)
export const useRouteGeometry = (routeId: number) => {
  return useQuery({
    queryKey: ['route', 'geometry', routeId],
    queryFn: () => routeService.getRouteGeoJSON(routeId),
    enabled: !!routeId,
    staleTime: Infinity, // Hình dáng tuyến đường ít khi đổi, cache vĩnh viễn
    select: (data: RouteGeoJSON) => {
      // Transform dữ liệu ngay ở đây: [lng, lat] -> [lat, lng]
      return data.coordinates.map(([lng, lat]) => [lat, lng] as [number, number]);
    },
  });
};

// 4. Lấy tất cả tuyến đường
export const useAllRoutes = () => {
  return useQuery({
    queryKey: ['routes', 'all'],
    queryFn: async () => {
      const result = await routeService.getAllRoutes();
      return result.routes;
    },
    staleTime: 1000 * 60 * 5, // Cache 5 minutes
  });
};

// 5. Lấy thông tin chi tiết tuyến đường
export const useRoute = (routeId: number) => {
  return useQuery({
    queryKey: ['route', routeId],
    queryFn: () => routeService.getRouteById(routeId),
    enabled: !!routeId,
    staleTime: 1000 * 60 * 5,
  });
};

// 6. Lấy các điểm dừng trên tuyến
export const useRouteStops = (routeId: number) => {
  return useQuery({
    queryKey: ['route', routeId, 'stops'],
    queryFn: () => routeService.getRouteStops(routeId),
    enabled: !!routeId,
    staleTime: 1000 * 60 * 5,
  });
};

// --- HOOKS CHO BUSES ---

// 7. Lấy tất cả xe bus đang hoạt động
export const useActiveBuses = () => {
  return useQuery({
    queryKey: ['buses', 'active'],
    queryFn: () => busService.getAllActiveBuses(),
    staleTime: 1000 * 10, // Cache 10 seconds (buses move)
    refetchInterval: 1000 * 30, // Auto-refresh every 30 seconds
  });
};

// 8. Lấy tất cả xe bus (bao gồm cả không hoạt động)
export const useAllBuses = (includeInactive: boolean = false) => {
  return useQuery({
    queryKey: ['buses', 'all', includeInactive],
    queryFn: async () => {
      const result = await busService.getAllBuses(undefined, 100, includeInactive);
      return result.buses;
    },
    staleTime: 1000 * 60 * 2,
  });
};

// 9. Lấy thông tin xe bus theo ID
export const useBus = (busId: number) => {
  return useQuery({
    queryKey: ['bus', busId],
    queryFn: () => busService.getBusById(busId),
    enabled: !!busId,
    staleTime: 1000 * 10,
    refetchInterval: 1000 * 15, // Refresh every 15 seconds for location updates
  });
};

// 10. Lấy các xe bus trên tuyến
export const useBusesByRoute = (routeId: number) => {
  return useQuery({
    queryKey: ['buses', 'route', routeId],
    queryFn: () => busService.getBusesByRoute(routeId),
    enabled: !!routeId,
    staleTime: 1000 * 10,
    refetchInterval: 1000 * 30,
  });
};

// 11. Tìm xe bus gần nhất
export const useNearestBuses = (
  lat: number,
  lng: number,
  routeId?: number,
  limit: number = 5,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: ['buses', 'nearest', lat, lng, routeId, limit],
    queryFn: () => busService.findNearestBuses(lat, lng, routeId, limit),
    enabled: enabled && !!lat && !!lng,
    staleTime: 1000 * 10,
    placeholderData: keepPreviousData,
  });
};

// 12. Lấy số lượng xe bus đang hoạt động
export const useActiveBusCount = () => {
  return useQuery({
    queryKey: ['buses', 'count', 'active'],
    queryFn: () => busService.getActiveBusCount(),
    staleTime: 1000 * 30,
  });
};

// 13. Kiểm tra xe bus có đang trên tuyến không
export const useBusOnRoute = (busId: number, toleranceMeters: number = 100) => {
  return useQuery({
    queryKey: ['bus', busId, 'on-route', toleranceMeters],
    queryFn: () => busService.checkBusOnRoute(busId, toleranceMeters),
    enabled: !!busId,
    staleTime: 1000 * 15,
  });
};

// 14. Lấy chi tiết vị trí xe bus
export const useBusLocationDetails = (busId: number) => {
  return useQuery({
    queryKey: ['bus', busId, 'location-details'],
    queryFn: () => busService.getBusLocationDetails(busId),
    enabled: !!busId,
    staleTime: 1000 * 10,
    refetchInterval: 1000 * 15,
  });
};

// --- MUTATIONS (Write Operations) ---

// 15. Cập nhật vị trí xe bus (for drivers)
export const useUpdateBusLocation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      busId,
      payload,
    }: {
      busId: number;
      payload: UpdateBusLocationPayload;
    }) => busService.updateBusLocation(busId, payload),
    onSuccess: (_, variables) => {
      // Invalidate related queries to refetch fresh data
      queryClient.invalidateQueries({ queryKey: ['bus', variables.busId] });
      queryClient.invalidateQueries({ queryKey: ['buses', 'active'] });
      queryClient.invalidateQueries({ queryKey: ['buses', 'nearest'] });
    },
  });
};