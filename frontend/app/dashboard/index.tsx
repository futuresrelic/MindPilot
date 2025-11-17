/**
 * Dashboard - Main home screen
 */
import { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl
} from 'react-native';
import { useRouter } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { LinearGradient } from 'expo-linear-gradient';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuthStore } from '../../state/authStore';
import { insightsAPI, moodAPI, habitsAPI } from '../../utils/api';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { colors, spacing, typography, borderRadius, shadows } from '../../utils/theme';

export default function Dashboard() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);

  const { data: dashboardData, refetch, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await insightsAPI.getDashboard();
      return response.data;
    }
  });

  const { data: todayMood } = useQuery({
    queryKey: ['todayMood'],
    queryFn: async () => {
      const response = await moodAPI.getToday();
      return response.data;
    }
  });

  const { data: habits } = useQuery({
    queryKey: ['habits'],
    queryFn: async () => {
      const response = await habitsAPI.getAll();
      return response.data;
    }
  });

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={isLoading} onRefresh={refetch} />
        }
      >
        {/* Header */}
        <LinearGradient
          colors={['#6FA8FF', '#B8A2FF']}
          style={styles.header}
        >
          <Text style={styles.greeting}>
            Hello, {user?.email?.split('@')[0] || 'there'} 👋
          </Text>
          <Text style={styles.streak}>🔥 {user?.daily_streak || 0} day streak</Text>
        </LinearGradient>

        <View style={styles.content}>
          {/* Mood Check-in Card */}
          <Card style={styles.moodCard}>
            <Text style={styles.cardTitle}>How are you feeling today?</Text>
            {todayMood?.logged_today ? (
              <View style={styles.moodLogged}>
                <Text style={styles.moodEmoji}>
                  {getMoodEmoji(todayMood.mood.mood_value)}
                </Text>
                <Text style={styles.moodText}>
                  You're feeling {todayMood.mood.mood_value}/10 today
                </Text>
                {todayMood.mood.ai_reflection && (
                  <Text style={styles.reflection}>
                    {todayMood.mood.ai_reflection}
                  </Text>
                )}
              </View>
            ) : (
              <Button
                title="Check in now"
                onPress={() => router.push('/mood')}
                style={styles.checkInButton}
              />
            )}
          </Card>

          {/* Habits Card */}
          <Card>
            <View style={styles.cardHeader}>
              <Text style={styles.cardTitle}>Today's Habits</Text>
              <TouchableOpacity onPress={() => router.push('/habits')}>
                <Text style={styles.seeAll}>See all →</Text>
              </TouchableOpacity>
            </View>

            {habits && habits.length > 0 ? (
              <View style={styles.habitsList}>
                <Text style={styles.habitsCount}>
                  {dashboardData?.today?.habits_completed || 0} of{' '}
                  {dashboardData?.today?.total_active_habits || 0} completed
                </Text>
              </View>
            ) : (
              <TouchableOpacity
                style={styles.createHabit}
                onPress={() => router.push('/habits')}
              >
                <Text style={styles.createHabitText}>+ Create your first habit</Text>
              </TouchableOpacity>
            )}
          </Card>

          {/* Quick Actions */}
          <View style={styles.quickActions}>
            <QuickActionButton
              icon="📝"
              label="Journal"
              onPress={() => router.push('/journal')}
            />
            <QuickActionButton
              icon="🎧"
              label="Meditation"
              onPress={() => router.push('/audio')}
            />
            <QuickActionButton
              icon="📊"
              label="Insights"
              onPress={() => router.push('/insights')}
            />
          </View>

          {/* Week Stats */}
          {dashboardData?.week && (
            <Card>
              <Text style={styles.cardTitle}>This Week</Text>
              <View style={styles.statsGrid}>
                <StatItem
                  label="Mood Logs"
                  value={dashboardData.week.mood_logs}
                  icon="😊"
                />
                <StatItem
                  label="Journal Entries"
                  value={dashboardData.week.journal_entries}
                  icon="📝"
                />
                <StatItem
                  label="Avg Mood"
                  value={dashboardData.week.avg_mood.toFixed(1)}
                  icon="📈"
                />
                <StatItem
                  label="Sleep Hours"
                  value={dashboardData.week.avg_sleep?.toFixed(1) || '—'}
                  icon="😴"
                />
              </View>
            </Card>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const QuickActionButton = ({ icon, label, onPress }: any) => (
  <TouchableOpacity style={styles.actionButton} onPress={onPress}>
    <Text style={styles.actionIcon}>{icon}</Text>
    <Text style={styles.actionLabel}>{label}</Text>
  </TouchableOpacity>
);

const StatItem = ({ label, value, icon }: any) => (
  <View style={styles.statItem}>
    <Text style={styles.statIcon}>{icon}</Text>
    <Text style={styles.statValue}>{value}</Text>
    <Text style={styles.statLabel}>{label}</Text>
  </View>
);

const getMoodEmoji = (value: number) => {
  if (value <= 2) return '😢';
  if (value <= 4) return '😔';
  if (value <= 6) return '😐';
  if (value <= 8) return '🙂';
  return '😄';
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.offWhite
  },
  header: {
    padding: spacing.xl,
    paddingBottom: spacing.xxl
  },
  greeting: {
    ...typography.h1,
    color: colors.white,
    marginBottom: spacing.xs
  },
  streak: {
    ...typography.body,
    color: colors.white,
    opacity: 0.9
  },
  content: {
    padding: spacing.md,
    gap: spacing.md
  },
  moodCard: {
    alignItems: 'center'
  },
  cardTitle: {
    ...typography.h3,
    marginBottom: spacing.md
  },
  moodLogged: {
    alignItems: 'center',
    gap: spacing.sm
  },
  moodEmoji: {
    fontSize: 64
  },
  moodText: {
    ...typography.body,
    color: colors.darkGray
  },
  reflection: {
    ...typography.bodySmall,
    color: colors.gray,
    textAlign: 'center',
    marginTop: spacing.sm,
    fontStyle: 'italic'
  },
  checkInButton: {
    width: '100%'
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md
  },
  seeAll: {
    color: colors.softBlue,
    fontSize: 14
  },
  habitsList: {
    gap: spacing.sm
  },
  habitsCount: {
    ...typography.body,
    color: colors.darkGray
  },
  createHabit: {
    padding: spacing.md,
    borderWidth: 2,
    borderColor: colors.lightGray,
    borderRadius: borderRadius.md,
    borderStyle: 'dashed',
    alignItems: 'center'
  },
  createHabitText: {
    color: colors.softBlue,
    fontSize: 16
  },
  quickActions: {
    flexDirection: 'row',
    gap: spacing.md
  },
  actionButton: {
    flex: 1,
    backgroundColor: colors.white,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    alignItems: 'center',
    gap: spacing.xs,
    ...shadows.small
  },
  actionIcon: {
    fontSize: 32
  },
  actionLabel: {
    ...typography.bodySmall,
    color: colors.darkGray
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md
  },
  statItem: {
    flex: 1,
    minWidth: '45%',
    alignItems: 'center',
    gap: spacing.xs
  },
  statIcon: {
    fontSize: 32
  },
  statValue: {
    ...typography.h2,
    color: colors.softBlue
  },
  statLabel: {
    ...typography.caption,
    color: colors.gray
  }
});
