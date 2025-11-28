// Domain Model (App sử dụng cái này)
export interface User {
  id: number;
  username: string;
  fullName: string;
  avatar: string;
  role: 'admin' | 'driver' | 'manager';
}

// DTOs (Data Transfer Objects - Dữ liệu thô từ API)
export interface LoginPayload {
  username: string;
  password: string;
}

// Giả sử API trả về field hơi khác, ví dụ snake_case
export interface LoginResponseDTO {
  access_token?: string; // Có thể có hoặc không (nếu dùng cookie)
  user_info: {
    id: number;
    user_name: string; // API trả về user_name
    full_name: string; // API trả về full_name
    role_id: string;
    avatar_url: string;
  };
}

// Legacy - kept for backward compatibility if needed
export interface LoginResponse {
  token: string;
  user: User;
}