/**
 * Mood Check-in Screen
 */
import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { LinearGradient } from 'expo-linear-gradient';
import { moodAPI } from '../../utils/api';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { colors, spacing, typography, borderRadius } from '../../utils/theme';

const MOOD_TAGS = [
  'Stressed',
  'Tired',
  'Anxious',
  'Happy',
  'Calm',
  'Focused',
  'Grateful',
  'Energized',
  'Sad',
  'Overwhelmed',
  'Content',
  'Motivated'
];

export default function MoodCheckIn() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [moodValue, setMoodValue] = useState(5);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [note, setNote] = useState('');

  const checkInMutation = useMutation({
    mutationFn: async () => {
      const response = await moodAPI.checkIn(moodValue, selectedTags, note || undefined);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['todayMood'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });

      Alert.alert(
        'Mood Logged! 🎉',
        data.ai_reflection,
        [{ text: 'Continue', onPress: () => router.back() }]
      );
    },
    onError: () => {
      Alert.alert('Error', 'Failed to log mood. Please try again.');
    }
  });

  const toggleTag = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const getMoodEmoji = () => {
    if (moodValue <= 2) return '😢';
    if (moodValue <= 4) return '😔';
    if (moodValue <= 6) return '😐';
    if (moodValue <= 8) return '🙂';
    return '😄';
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView>
        <LinearGradient
          colors={['#6FA8FF', '#B8A2FF']}
          style={styles.header}
        >
          <TouchableOpacity onPress={() => router.back()} style={styles.back}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>How are you feeling?</Text>
        </LinearGradient>

        <View style={styles.content}>
          {/* Mood Slider */}
          <Card>
            <View style={styles.moodSection}>
              <Text style={styles.moodEmoji}>{getMoodEmoji()}</Text>
              <Text style={styles.moodValue}>{moodValue} / 10</Text>

              <View style={styles.sliderContainer}>
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((value) => (
                  <TouchableOpacity
                    key={value}
                    style={[
                      styles.sliderDot,
                      moodValue >= value && styles.sliderDotActive
                    ]}
                    onPress={() => setMoodValue(value)}
                  />
                ))}
              </View>

              <View style={styles.sliderLabels}>
                <Text style={styles.sliderLabel}>Very Low</Text>
                <Text style={styles.sliderLabel}>Amazing</Text>
              </View>
            </View>
          </Card>

          {/* Tags */}
          <Card>
            <Text style={styles.sectionTitle}>How would you describe it?</Text>
            <View style={styles.tagsContainer}>
              {MOOD_TAGS.map((tag) => (
                <TouchableOpacity
                  key={tag}
                  style={[
                    styles.tag,
                    selectedTags.includes(tag) && styles.tagActive
                  ]}
                  onPress={() => toggleTag(tag)}
                >
                  <Text
                    style={[
                      styles.tagText,
                      selectedTags.includes(tag) && styles.tagTextActive
                    ]}
                  >
                    {tag}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </Card>

          {/* Note */}
          <Card>
            <Text style={styles.sectionTitle}>Any thoughts? (Optional)</Text>
            <TextInput
              style={styles.textInput}
              placeholder="What's on your mind?"
              placeholderTextColor={colors.gray}
              multiline
              numberOfLines={4}
              value={note}
              onChangeText={setNote}
              textAlignVertical="top"
            />
          </Card>

          <Button
            title="Save Mood Check-in"
            onPress={() => checkInMutation.mutate()}
            loading={checkInMutation.isPending}
            style={styles.submitButton}
          />
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
    color: colors.white
  },
  content: {
    padding: spacing.md,
    gap: spacing.md
  },
  moodSection: {
    alignItems: 'center',
    gap: spacing.md
  },
  moodEmoji: {
    fontSize: 80
  },
  moodValue: {
    ...typography.h2,
    color: colors.softBlue
  },
  sliderContainer: {
    flexDirection: 'row',
    gap: spacing.sm,
    marginVertical: spacing.lg
  },
  sliderDot: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.lightGray
  },
  sliderDotActive: {
    backgroundColor: colors.softBlue
  },
  sliderLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%'
  },
  sliderLabel: {
    ...typography.caption,
    color: colors.gray
  },
  sectionTitle: {
    ...typography.h3,
    marginBottom: spacing.md
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm
  },
  tag: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.full,
    backgroundColor: colors.lightGray,
    borderWidth: 2,
    borderColor: 'transparent'
  },
  tagActive: {
    backgroundColor: colors.softBlue,
    borderColor: colors.softBlue
  },
  tagText: {
    color: colors.darkGray,
    fontSize: 14
  },
  tagTextActive: {
    color: colors.white,
    fontWeight: '600'
  },
  textInput: {
    backgroundColor: colors.offWhite,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    fontSize: 16,
    minHeight: 100
  },
  submitButton: {
    marginTop: spacing.md
  }
});
