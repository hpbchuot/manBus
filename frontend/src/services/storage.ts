// src/services/storage.ts

const USER_KEY = 'user_info';

const storage = {
  // --- CHỈ CÒN QUẢN LÝ USER INFO (UI STATE) ---
  getUser: (): any | null => {
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  },

  setUser: (user: any): void => {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  
  clearUser: (): void => {
    localStorage.removeItem(USER_KEY);
  },
};

export default storage;