import type { IHttpClient } from '@/types/http';
import type { ApiResponse } from '@/services/api';
import type { IAuthAdapter } from '@/services/adapters/authAdapter';
import type { LoginPayload, RegisterPayload, LoginResponseDTO, User } from '@/types/auth';

export interface IAuthService {
  register(payload: RegisterPayload): Promise<User>;
  login(payload: LoginPayload): Promise<User>;
  logout(): Promise<void>;
}

export class AuthService implements IAuthService {
  constructor(
    private http: IHttpClient,   // Inject HttpClient
    private adapter: IAuthAdapter // Inject Adapter
  ) {}

  async register(payload: RegisterPayload): Promise<User> {
    const response = await this.http.post<ApiResponse<LoginResponseDTO>>('/auth/register', payload);
    return this.adapter.toUser(response.data);
  }

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
