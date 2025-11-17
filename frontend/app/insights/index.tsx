/**
 * Insights & Analytics Screen
 */
import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Dimensions,
  ActivityIndicator
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { LinearGradient } from 'expo-linear-gradient';
import { VictoryLine, VictoryChart, VictoryTheme, VictoryAxis } from 'victory-native';
import { moodAPI, insightsAPI } from '../../utils/api';
import { Card } from '../../components/ui/Card';
import { colors, spacing, typography } from '../../utils/theme';

const screenWidth = Dimensions.get('window').width;

export default function Insights() {
  const router = useRouter();
  const [period, setPeriod] = useState(30);

  const { data: moodHistory, isLoading: moodLoading } = useQuery({
    queryKey: ['mood-history', period],
    queryFn: async () => {
      const response = await moodAPI.getHistory(period);
      return response.data;
    }
  });

  const { data: moodPatterns } = useQuery({
    queryKey: ['mood-patterns', period],
    queryFn: async () => {
      const response = await moodAPI.getPatterns(period);
      return response.data;
    }
  });

  const { data: weeklyInsight } = useQuery({
    queryKey: ['weekly-insight'],
    queryFn: async () => {
      const response = await insightsAPI.getWeekly();
      return response.data;
    },
    enabled: false  // Only fetch on premium
  });

  // Prepare chart data
  const chartData = moodHistory?.moods
    ?.slice(0, 14)
    ?.reverse()
    ?.map((mood: any, index: number) => ({
      x: index + 1,
      y: mood.mood_value
    })) || [];

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView>
        <LinearGradient
          colors={['#FF9FB0', '#B8A2FF']}
          style={styles.header}
        >
          <TouchableOpacity onPress={() => router.back()} style={styles.back}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>📊 Insights</Text>
          <Text style={styles.subtitle}>Your wellness journey at a glance</Text>
        </LinearGradient>

        <View style={styles.content}>
          {/* Period Selector */}
          <View style={styles.periodSelector}>
            {[7, 30, 90].map((days) => (
              <TouchableOpacity
                key={days}
                style={[
                  styles.periodButton,
                  period === days && styles.periodButtonActive
                ]}
                onPress={() => setPeriod(days)}
              >
                <Text
                  style={[
                    styles.periodText,
                    period === days && styles.periodTextActive
                  ]}
                >
                  {days}d
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Mood Chart */}
          <Card>
            <Text style={styles.cardTitle}>Mood Trend</Text>
            {moodLoading ? (
              <ActivityIndicator size="large" color={colors.softBlue} />
            ) : chartData.length > 0 ? (
              <VictoryChart
                theme={VictoryTheme.material}
                width={screenWidth - spacing.md * 4}
                height={200}
              >
                <VictoryAxis
                  style={{
                    axis: { stroke: colors.lightGray },
                    tickLabels: { fill: colors.gray, fontSize: 10 }
                  }}
                />
                <VictoryAxis
                  dependentAxis
                  domain={[0, 10]}
                  style={{
                    axis: { stroke: colors.lightGray },
                    tickLabels: { fill: colors.gray, fontSize: 10 }
                  }}
                />
                <VictoryLine
                  data={chartData}
                  style={{
                    data: { stroke: colors.softBlue, strokeWidth: 3 },
                    parent: { border: `1px solid ${colors.lightGray}` }
                  }}
                  animate={{
                    duration: 500,
                    onLoad: { duration: 500 }
                  }}
                />
              </VictoryChart>
            ) : (
              <Text style={styles.noData}>
                Not enough data yet. Keep logging your mood!
              </Text>
            )}
          </Card>

          {/* Mood Patterns */}
          {moodPatterns?.patterns && (
            <Card>
              <Text style={styles.cardTitle}>Mood Patterns</Text>

              <View style={styles.statsGrid}>
                <StatBox
                  label="Average Mood"
                  value={moodPatterns.patterns.average.toFixed(1)}
                  icon="😊"
                />
                <StatBox
                  label="Total Logs"
                  value={moodPatterns.patterns.total_logs}
                  icon="📝"
                />
                <StatBox
                  label="Trend"
                  value={moodPatterns.patterns.trend}
                  icon="📈"
                />
                <StatBox
                  label="Consistency"
                  value={moodPatterns.patterns.consistency.toFixed(1)}
                  icon="✨"
                />
              </View>

              {moodPatterns.patterns.common_tags?.length > 0 && (
                <View style={styles.tagsSection}>
                  <Text style={styles.tagsLabel}>Common feelings:</Text>
                  <View style={styles.tags}>
                    {moodPatterns.patterns.common_tags.map((tag: string) => (
                      <View key={tag} style={styles.tag}>
                        <Text style={styles.tagText}>{tag}</Text>
                      </View>
                    ))}
                  </View>
                </View>
              )}
            </Card>
          )}

          {/* Weekly Insight (Premium) */}
          <Card style={styles.premiumCard}>
            <Text style={styles.premiumTitle}>📊 Weekly Wellness Report</Text>
            <Text style={styles.premiumText}>
              Get AI-powered weekly summaries with personalized insights,
              trends, and recommendations.
            </Text>
            <TouchableOpacity
              style={styles.upgradeButton}
              onPress={() => router.push('/paywall')}
            >
              <Text style={styles.upgradeText}>Upgrade to Premium ✨</Text>
            </TouchableOpacity>
          </Card>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const StatBox = ({ label, value, icon }: any) => (
  <View style={styles.statBox}>
    <Text style={styles.statIcon}>{icon}</Text>
    <Text style={styles.statValue}>{value}</Text>
    <Text style={styles.statLabel}>{label}</Text>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.offWhite
  },
  header: {
    padding: spacing.xl,
    paddingBottom: spacing.xxl
  },
  back: {
    marginBottom: spacing.md
  },
  backText: {
    color: colors.white,
    fontSize: 16
  },
  title: {
    ...typography.h1,
    color: colors.white,
    marginBottom: spacing.xs
  },
  subtitle: {
    ...typography.body,
    color: colors.white,
    opacity: 0.9
  },
  content: {
    padding: spacing.md,
    gap: spacing.md
  },
  periodSelector: {
    flexDirection: 'row',
    gap: spacing.sm,
    backgroundColor: colors.white,
    borderRadius: 12,
    padding: 4
  },
  periodButton: {
    flex: 1,
    paddingVertical: spacing.sm,
    alignItems: 'center',
    borderRadius: 8
  },
  periodButtonActive: {
    backgroundColor: colors.softBlue
  },
  periodText: {
    color: colors.gray,
    fontWeight: '600'
  },
  periodTextActive: {
    color: colors.white
  },
  cardTitle: {
    ...typography.h3,
    marginBottom: spacing.md
  },
  noData: {
    ...typography.body,
    color: colors.gray,
    textAlign: 'center',
    padding: spacing.xl
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.md
  },
  statBox: {
    flex: 1,
    minWidth: '45%',
    alignItems: 'center',
    padding: spacing.md,
    backgroundColor: colors.offWhite,
    borderRadius: 12
  },
  statIcon: {
    fontSize: 24,
    marginBottom: spacing.xs
  },
  statValue: {
    ...typography.h2,
    color: colors.softBlue,
    marginBottom: spacing.xs
  },
  statLabel: {
    ...typography.caption,
    color: colors.gray,
    textTransform: 'capitalize'
  },
  tagsSection: {
    marginTop: spacing.md
  },
  tagsLabel: {
    ...typography.bodySmall,
    color: colors.gray,
    marginBottom: spacing.sm
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm
  },
  tag: {
    backgroundColor: colors.softBlue,
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 12
  },
  tagText: {
    color: colors.white,
    fontSize: 12
  },
  premiumCard: {
    backgroundColor: '#F0F9FF',
    borderWidth: 2,
    borderColor: colors.softBlue,
    alignItems: 'center'
  },
  premiumTitle: {
    ...typography.h3,
    color: colors.softBlue,
    marginBottom: spacing.sm
  },
  premiumText: {
    ...typography.body,
    color: colors.darkGray,
    textAlign: 'center',
    marginBottom: spacing.lg
  },
  upgradeButton: {
    backgroundColor: colors.softBlue,
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.xl,
    borderRadius: 24
  },
  upgradeText: {
    color: colors.white,
    fontWeight: '600',
    fontSize: 16
  }
});
