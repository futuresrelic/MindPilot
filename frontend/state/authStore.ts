/**
 * Authentication state management
 */
import { create } from 'zustand';
import * as SecureStore from 'expo-secure-store';

interface User {
  id: number;
  email: string;
  age_range?: string;
  goals?: string[];
  subscription_status: string;
  daily_streak: number;
  theme?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user: User) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (user: User) => void;
  loadToken: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (token: string, user: User) => {
    await SecureStore.setItemAsync('auth_token', token);
    await SecureStore.setItemAsync('user_data', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },

  logout: async () => {
    await SecureStore.deleteItemAsync('auth_token');
    await SecureStore.deleteItemAsync('user_data');
    set({ token: null, user: null, isAuthenticated: false });
  },

  updateUser: (user: User) => {
    set({ user });
    SecureStore.setItemAsync('user_data', JSON.stringify(user));
  },

  loadToken: async () => {
    try {
      const token = await SecureStore.getItemAsync('auth_token');
      const userData = await SecureStore.getItemAsync('user_data');

      if (token && userData) {
        set({
          token,
          user: JSON.parse(userData),
          isAuthenticated: true,
          isLoading: false
        });
      } else {
        set({ isLoading: false });
      }
    } catch (error) {
      console.error('Error loading auth token:', error);
      set({ isLoading: false });
    }
  }
}));
