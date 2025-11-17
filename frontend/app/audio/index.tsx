/**
 * Audio & Meditation Library
 */
import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { Audio } from 'expo-av';
import { LinearGradient } from 'expo-linear-gradient';
import { audioAPI } from '../../utils/api';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { colors, spacing, typography, borderRadius } from '../../utils/theme';

export default function AudioLibrary() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const [playingId, setPlayingId] = useState<number | null>(null);
  const [sound, setSound] = useState<Audio.Sound | null>(null);

  const { data: categories } = useQuery({
    queryKey: ['audio-categories'],
    queryFn: async () => {
      const response = await audioAPI.getCategories();
      return response.data;
    }
  });

  const { data: content, isLoading } = useQuery({
    queryKey: ['audio-content', selectedCategory],
    queryFn: async () => {
      const response = await audioAPI.getContent(selectedCategory);
      return response.data;
    }
  });

  const playAudio = async (audioItem: any) => {
    try {
      // Stop current audio if playing
      if (sound) {
        await sound.stopAsync();
        await sound.unloadAsync();
      }

      // Load and play new audio
      const { sound: newSound } = await Audio.Sound.createAsync(
        { uri: audioItem.audio_url },
        { shouldPlay: true }
      );

      setSound(newSound);
      setPlayingId(audioItem.id);

      newSound.setOnPlaybackStatusUpdate((status: any) => {
        if (status.didJustFinish) {
          setPlayingId(null);
          // Log session
          audioAPI.createSession({
            audio_id: audioItem.id.toString(),
            duration_seconds: Math.floor(status.positionMillis / 1000),
            completed: true
          });
        }
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to play audio');
    }
  };

  const stopAudio = async () => {
    if (sound) {
      await sound.stopAsync();
      await sound.unloadAsync();
      setPlayingId(null);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView>
        <LinearGradient
          colors={['#B8A2FF', '#6FA8FF']}
          style={styles.header}
        >
          <TouchableOpacity onPress={() => router.back()} style={styles.back}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>🎧 Audio Library</Text>
          <Text style={styles.subtitle}>Guided sessions for your wellbeing</Text>
        </LinearGradient>

        <View style={styles.content}>
          {/* Categories */}
          {categories && categories.categories && (
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              style={styles.categoriesScroll}
            >
              <TouchableOpacity
                style={[
                  styles.categoryChip,
                  !selectedCategory && styles.categoryChipActive
                ]}
                onPress={() => setSelectedCategory(undefined)}
              >
                <Text
                  style={[
                    styles.categoryText,
                    !selectedCategory && styles.categoryTextActive
                  ]}
                >
                  All
                </Text>
              </TouchableOpacity>

              {categories.categories.map((cat: string) => (
                <TouchableOpacity
                  key={cat}
                  style={[
                    styles.categoryChip,
                    selectedCategory === cat && styles.categoryChipActive
                  ]}
                  onPress={() => setSelectedCategory(cat)}
                >
                  <Text
                    style={[
                      styles.categoryText,
                      selectedCategory === cat && styles.categoryTextActive
                    ]}
                  >
                    {cat}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          )}

          {/* Audio List */}
          {isLoading ? (
            <ActivityIndicator size="large" color={colors.softBlue} />
          ) : content && content.content && content.content.length > 0 ? (
            content.content.map((item: any) => (
              <Card key={item.id} style={styles.audioCard}>
                <View style={styles.audioInfo}>
                  <Text style={styles.audioTitle}>{item.title}</Text>
                  {item.description && (
                    <Text style={styles.audioDescription}>
                      {item.description}
                    </Text>
                  )}

                  <View style={styles.audioMeta}>
                    <Text style={styles.audioDuration}>
                      ⏱️ {formatDuration(item.duration_seconds)}
                    </Text>
                    <Text style={styles.audioCategory}>
                      {item.category}
                    </Text>
                    {item.is_premium && (
                      <Text style={styles.premiumBadge}>Premium ✨</Text>
                    )}
                  </View>
                </View>

                <TouchableOpacity
                  style={[
                    styles.playButton,
                    playingId === item.id && styles.playButtonActive
                  ]}
                  onPress={() => {
                    if (playingId === item.id) {
                      stopAudio();
                    } else {
                      playAudio(item);
                    }
                  }}
                >
                  <Text style={styles.playIcon}>
                    {playingId === item.id ? '⏸' : '▶️'}
                  </Text>
                </TouchableOpacity>
              </Card>
            ))
          ) : (
            <Text style={styles.noContent}>
              No audio content available in this category
            </Text>
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
  categoriesScroll: {
    flexGrow: 0,
    marginBottom: spacing.md
  },
  categoryChip: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: borderRadius.full,
    backgroundColor: colors.white,
    marginRight: spacing.sm
  },
  categoryChipActive: {
    backgroundColor: colors.softBlue
  },
  categoryText: {
    color: colors.darkGray,
    fontSize: 14,
    fontWeight: '500'
  },
  categoryTextActive: {
    color: colors.white
  },
  audioCard: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm
  },
  audioInfo: {
    flex: 1,
    marginRight: spacing.md
  },
  audioTitle: {
    ...typography.h3,
    marginBottom: spacing.xs,
    fontSize: 16
  },
  audioDescription: {
    ...typography.bodySmall,
    color: colors.gray,
    marginBottom: spacing.sm
  },
  audioMeta: {
    flexDirection: 'row',
    gap: spacing.md,
    flexWrap: 'wrap'
  },
  audioDuration: {
    ...typography.caption,
    color: colors.darkGray
  },
  audioCategory: {
    ...typography.caption,
    color: colors.softBlue,
    textTransform: 'capitalize'
  },
  premiumBadge: {
    ...typography.caption,
    color: colors.lavender,
    fontWeight: '600'
  },
  playButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: colors.softBlue,
    alignItems: 'center',
    justifyContent: 'center'
  },
  playButtonActive: {
    backgroundColor: colors.lavender
  },
  playIcon: {
    fontSize: 20
  },
  noContent: {
    ...typography.body,
    color: colors.gray,
    textAlign: 'center',
    marginTop: spacing.xl
  }
});
