

// 1. Domain Model (App sử dụng)
export interface BusRoute {
  id: number;
  code: string;       // "01", "02"...
  name: string;       // "Tuyến 01 - Chiều đi"
  direction: string;  // "Chiều đi" | "Chiều về"
  distance: number;   // km (được tính từ mét)
  stopCount: number;  // Số điểm dừng
  price: number;      // (Mock data)
  operationTime: string; // (Mock data)
}

// 2. DTO (Data Transfer Object - Khớp 100% với API response)
export interface BusRouteDTO {
  route_id: number;
  route_length_meters: number;
  route_name: string; // "Route 01 1"
  stop_count: number;
}

// Interface cho response bọc ngoài (Wrapper)
export interface BusRouteListResponse {
  data: BusRouteDTO[];
}