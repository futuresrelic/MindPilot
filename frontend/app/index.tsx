/**
 * App entry point - handles auth routing
 */
import { useEffect } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuthStore } from '../state/authStore';
import { colors, spacing } from '../utils/theme';

export default function Index() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.replace('/dashboard');
      } else {
        router.replace('/onboarding');
      }
    }
  }, [isAuthenticated, isLoading]);

  return (
    <LinearGradient
      colors={['#6FA8FF', '#B8A2FF']}
      style={styles.container}
    >
      <ActivityIndicator size="large" color={colors.white} />
      <Text style={styles.text}>MindPilot</Text>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    gap: spacing.lg
  },
  text: {
    fontSize: 32,
    fontWeight: '700',
    color: colors.white
  }
});
