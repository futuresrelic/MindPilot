/**
 * Onboarding screen - Login/Signup
 */
import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  TouchableOpacity,
  Alert
} from 'react-native';
import { useRouter } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { useAuthStore } from '../../state/authStore';
import { authAPI } from '../../utils/api';
import { Button } from '../../components/ui/Button';
import { colors, spacing, borderRadius, typography } from '../../utils/theme';

export default function Onboarding() {
  const router = useRouter();
  const login = useAuthStore((state) => state.login);

  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAuth = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);

    try {
      const response = isLogin
        ? await authAPI.login(email, password)
        : await authAPI.signup(email, password);

      const { access_token, user } = response.data;
      await login(access_token, user);

      router.replace('/dashboard');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient
      colors={['#6FA8FF', '#B8A2FF']}
      style={styles.container}
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.header}>
            <Text style={styles.logo}>🧠</Text>
            <Text style={styles.title}>MindPilot</Text>
            <Text style={styles.subtitle}>
              Your AI companion for mental wellness
            </Text>
          </View>

          <View style={styles.form}>
            <TextInput
              style={styles.input}
              placeholder="Email"
              placeholderTextColor={colors.gray}
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              keyboardType="email-address"
            />

            <TextInput
              style={styles.input}
              placeholder="Password"
              placeholderTextColor={colors.gray}
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              autoCapitalize="none"
            />

            <Button
              title={isLogin ? 'Sign In' : 'Create Account'}
              onPress={handleAuth}
              loading={loading}
              style={styles.button}
            />

            <TouchableOpacity onPress={() => setIsLogin(!isLogin)}>
              <Text style={styles.switchText}>
                {isLogin
                  ? "Don't have an account? Sign Up"
                  : 'Already have an account? Sign In'}
              </Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1
  },
  keyboardView: {
    flex: 1
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: spacing.xl
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing.xxl
  },
  logo: {
    fontSize: 80,
    marginBottom: spacing.md
  },
  title: {
    ...typography.h1,
    color: colors.white,
    marginBottom: spacing.sm
  },
  subtitle: {
    ...typography.body,
    color: colors.white,
    opacity: 0.9,
    textAlign: 'center'
  },
  form: {
    gap: spacing.md
  },
  input: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    fontSize: 16,
    color: colors.black
  },
  button: {
    marginTop: spacing.md,
    backgroundColor: colors.white
  },
  switchText: {
    color: colors.white,
    textAlign: 'center',
    marginTop: spacing.md,
    fontSize: 14
  }
});
