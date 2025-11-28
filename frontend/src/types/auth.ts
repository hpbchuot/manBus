export interface User {
  id: string | number;
  username: string;
  fullName: string;
  role: 'admin' | 'user' | 'driver';
}

export interface LoginPayload {
  username: string;
  password: string; 
}

export interface LoginResponse {
  token: string;
  user: User;
}