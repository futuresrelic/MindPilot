/**
 * AI Journal Screen
 */
import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
  ActivityIndicator
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { LinearGradient } from 'expo-linear-gradient';
import { journalAPI } from '../../utils/api';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { colors, spacing, typography, borderRadius } from '../../utils/theme';

export default function Journal() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [entryText, setEntryText] = useState('');
  const [showAI, setShowAI] = useState(false);
  const [aiResult, setAiResult] = useState<any>(null);

  const { data: entries, isLoading } = useQuery({
    queryKey: ['journal-entries'],
    queryFn: async () => {
      const response = await journalAPI.getEntries(10);
      return response.data;
    }
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      const response = await journalAPI.createEntry(entryText);
      return response.data;
    },
    onSuccess: (data) => {
      setAiResult(data);
      setShowAI(true);
      setEntryText('');
      queryClient.invalidateQueries({ queryKey: ['journal-entries'] });
    },
    onError: (error: any) => {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to save journal entry');
    }
  });

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView>
        <LinearGradient
          colors={['#74E4D4', '#6FA8FF']}
          style={styles.header}
        >
          <TouchableOpacity onPress={() => router.back()} style={styles.back}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>AI Journal</Text>
          <Text style={styles.subtitle}>Reflect with your AI companion</Text>
        </LinearGradient>

        <View style={styles.content}>
          {/* Write Entry */}
          <Card>
            <Text style={styles.sectionTitle}>What's on your mind?</Text>
            <TextInput
              style={styles.textArea}
              placeholder="Start writing... Share your thoughts, feelings, or experiences from today."
              placeholderTextColor={colors.gray}
              multiline
              numberOfLines={8}
              value={entryText}
              onChangeText={setEntryText}
              textAlignVertical="top"
            />

            <Button
              title="Reflect with AI ✨"
              onPress={() => createMutation.mutate()}
              loading={createMutation.isPending}
              disabled={entryText.length < 10}
              style={styles.submitButton}
            />
          </Card>

          {/* AI Response */}
          {showAI && aiResult && (
            <Card style={styles.aiCard}>
              <Text style={styles.aiTitle}>AI Reflection</Text>

              <View style={styles.aiSection}>
                <Text style={styles.aiLabel}>Summary</Text>
                <Text style={styles.aiText}>{aiResult.ai_summary}</Text>
              </View>

              {aiResult.themes && aiResult.themes.length > 0 && (
                <View style={styles.aiSection}>
                  <Text style={styles.aiLabel}>Themes</Text>
                  <View style={styles.themesContainer}>
                    {aiResult.themes.map((theme: string, index: number) => (
                      <View key={index} style={styles.theme}>
                        <Text style={styles.themeText}>{theme}</Text>
                      </View>
                    ))}
                  </View>
                </View>
              )}

              {aiResult.ai_cbt_suggestion && (
                <View style={styles.aiSection}>
                  <Text style={styles.aiLabel}>Supportive Insight</Text>
                  <Text style={styles.aiText}>{aiResult.ai_cbt_suggestion}</Text>
                </View>
              )}

              <TouchableOpacity
                style={styles.closeAI}
                onPress={() => setShowAI(false)}
              >
                <Text style={styles.closeAIText}>Continue</Text>
              </TouchableOpacity>
            </Card>
          )}

          {/* Past Entries */}
          <Text style={styles.historyTitle}>Recent Entries</Text>

          {isLoading ? (
            <ActivityIndicator size="large" color={colors.softBlue} />
          ) : entries && entries.entries.length > 0 ? (
            entries.entries.map((entry: any) => (
              <Card key={entry.id} style={styles.entryCard}>
                <Text style={styles.entryDate}>
                  {new Date(entry.created_at).toLocaleDateString()}
                </Text>
                <Text style={styles.entryText} numberOfLines={3}>
                  {entry.text}
                </Text>
                {entry.ai_summary && (
                  <Text style={styles.entrySummary}>{entry.ai_summary}</Text>
                )}
              </Card>
            ))
          ) : (
            <Text style={styles.noEntries}>No entries yet. Start journaling! 📝</Text>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

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
  sectionTitle: {
    ...typography.h3,
    marginBottom: spacing.md
  },
  textArea: {
    backgroundColor: colors.offWhite,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    fontSize: 16,
    minHeight: 200,
    marginBottom: spacing.md
  },
  submitButton: {
    marginTop: spacing.sm
  },
  aiCard: {
    backgroundColor: '#F0F9FF',
    borderColor: colors.softBlue,
    borderWidth: 2
  },
  aiTitle: {
    ...typography.h3,
    color: colors.softBlue,
    marginBottom: spacing.md
  },
  aiSection: {
    marginBottom: spacing.md
  },
  aiLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.gray,
    marginBottom: spacing.xs,
    textTransform: 'uppercase'
  },
  aiText: {
    ...typography.body,
    color: colors.darkGray,
    fontStyle: 'italic'
  },
  themesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm
  },
  theme: {
    backgroundColor: colors.softBlue,
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: borderRadius.full
  },
  themeText: {
    color: colors.white,
    fontSize: 12
  },
  closeAI: {
    alignItems: 'center',
    marginTop: spacing.md
  },
  closeAIText: {
    color: colors.softBlue,
    fontWeight: '600'
  },
  historyTitle: {
    ...typography.h3,
    marginTop: spacing.lg,
    marginBottom: spacing.sm
  },
  entryCard: {
    marginBottom: spacing.sm
  },
  entryDate: {
    ...typography.caption,
    color: colors.gray,
    marginBottom: spacing.xs
  },
  entryText: {
    ...typography.body,
    color: colors.darkGray
  },
  entrySummary: {
    ...typography.bodySmall,
    color: colors.gray,
    marginTop: spacing.sm,
    fontStyle: 'italic'
  },
  noEntries: {
    ...typography.body,
    color: colors.gray,
    textAlign: 'center',
    marginTop: spacing.lg
  }
});
