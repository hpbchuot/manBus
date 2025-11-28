import { useQuery, keepPreviousData } from '@tanstack/react-query';
import api from '@/services/api';
import { StopService } from '@/services/api/stopApi';
import { StopAdapter } from '@/services/adapters/stopAdapter';
import { RouteService } from '@/services/api/routeApi';
import { RouteAdapter } from '@/services/adapters/routeAdapter';
import type { Stop, NearestStop } from '@/types/stop';
import type { RouteGeoJSON } from '@/types/route';

// Khởi tạo Service (Singleton instances)
// Việc này đảm bảo chúng ta không tạo mới instance mỗi lần render
const stopAdapter = new StopAdapter();
const stopService = new StopService(api, stopAdapter);

const routeAdapter = new RouteAdapter();
const routeService = new RouteService(api, routeAdapter);

// --- HOOKS CHO STOPS ---

// 1. Lấy tất cả trạm (Có cache)
export const useAllStops = () => {
  return useQuery({
    queryKey: ['stops', 'all'],
    queryFn: () => stopService.getAllStops(),
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