/**
 * Root layout for Expo Router
 */
import { useEffect } from 'react';
import { Stack } from 'expo-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StatusBar } from 'expo-status-bar';
import { useAuthStore } from '../state/authStore';

const queryClient = new QueryClient();

export default function RootLayout() {
  const loadToken = useAuthStore((state) => state.loadToken);

  useEffect(() => {
    loadToken();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <StatusBar style="auto" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: '#F8F9FA' }
        }}
      >
        <Stack.Screen name="index" />
        <Stack.Screen name="onboarding" />
        <Stack.Screen name="dashboard" />
        <Stack.Screen name="mood" />
        <Stack.Screen name="journal" />
        <Stack.Screen name="habits" />
        <Stack.Screen name="audio" />
        <Stack.Screen name="insights" />
        <Stack.Screen name="paywall" />
      </Stack>
    </QueryClientProvider>
  );
}
