import { IHttpClient } from '@/types/http';
import { ApiResponse } from '@/services/api';
import { IAuthAdapter } from './authAdapter';
import { LoginPayload, LoginResponseDTO, User } from './types';

export interface IAuthService {
  login(payload: LoginPayload): Promise<User>;
  logout(): Promise<void>;
  getCurrentUser(): Promise<User>;
}

export class AuthService implements IAuthService {
  constructor(
    private http: IHttpClient,   // Inject HttpClient
    private adapter: IAuthAdapter // Inject Adapter
  ) {}

  async login(payload: LoginPayload): Promise<User> {
    // 1. Gọi API nhận dữ liệu thô
    const response = await this.http.post<ApiResponse<LoginResponseDTO>>('/auth/login', payload);
    
    // 2. Dùng Adapter chuyển đổi dữ liệu thô thành Domain User
    // Service không được trả về "response.data" trực tiếp như trước
    return this.adapter.toUser(response.data);
  }

  async logout(): Promise<void> {
    await this.http.post('/auth/logout');
  }


}