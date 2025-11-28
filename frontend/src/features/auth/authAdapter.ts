import type { LoginResponseDTO, User } from './types';

// Interface quy định hành vi convert
export interface IAuthAdapter {
  toUser(dto: LoginResponseDTO): User;
}

export class AuthAdapter implements IAuthAdapter {
  // Chuyển đổi từ DTO (Backend) sang Domain Model (Frontend)
  toUser(dto: LoginResponseDTO): User {
    const rawUser = dto.user_info;
    
    return {
      id: rawUser.id,
      username: rawUser.user_name, // Mapping: user_name -> username
      fullName: rawUser.full_name, // Mapping: full_name -> fullName
      role: rawUser.role_id as 'admin' | 'driver' | 'manager',
      avatar: rawUser.avatar_url || '/assets/default-avatar.png', // Xử lý fallback logic
    };
  }
}