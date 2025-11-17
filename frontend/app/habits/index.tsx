/**
 * Habits Tracker Screen
 */
import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Modal,
  Alert
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { LinearGradient } from 'expo-linear-gradient';
import { habitsAPI } from '../../utils/api';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { colors, spacing, typography, borderRadius } from '../../utils/theme';

export default function Habits() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const [showModal, setShowModal] = useState(false);
  const [newHabit, setNewHabit] = useState({ title: '', description: '' });

  const { data: habits, isLoading } = useQuery({
    queryKey: ['habits'],
    queryFn: async () => {
      const response = await habitsAPI.getAll();
      return response.data;
    }
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      const response = await habitsAPI.create(newHabit);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
      setShowModal(false);
      setNewHabit({ title: '', description: '' });
    },
    onError: (error: any) => {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create habit');
    }
  });

  const completeMutation = useMutation({
    mutationFn: async (habitId: number) => {
      const response = await habitsAPI.complete(habitId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    }
  });

  const uncompleteMutation = useMutation({
    mutationFn: async (habitId: number) => {
      const response = await habitsAPI.uncomplete(habitId);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['habits'] });
    }
  });

  const isCompletedToday = (lastCompleted: string | null) => {
    if (!lastCompleted) return false;
    const today = new Date().toDateString();
    const completed = new Date(lastCompleted).toDateString();
    return today === completed;
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView>
        <LinearGradient
          colors={['#B8A2FF', '#FF9FB0']}
          style={styles.header}
        >
          <TouchableOpacity onPress={() => router.back()} style={styles.back}>
            <Text style={styles.backText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Habit Tracker</Text>
          <Text style={styles.subtitle}>Build consistency, one day at a time</Text>
        </LinearGradient>

        <View style={styles.content}>
          <Button
            title="+ Create New Habit"
            onPress={() => setShowModal(true)}
            style={styles.createButton}
          />

          {habits && habits.length > 0 ? (
            habits.map((habit: any) => {
              const completed = isCompletedToday(habit.last_completed);

              return (
                <Card key={habit.id} style={styles.habitCard}>
                  <View style={styles.habitHeader}>
                    <View style={styles.habitInfo}>
                      <Text style={styles.habitTitle}>{habit.title}</Text>
                      {habit.description && (
                        <Text style={styles.habitDescription}>
                          {habit.description}
                        </Text>
                      )}
                      <Text style={styles.habitStreak}>
                        🔥 {habit.streak} day streak • Best: {habit.best_streak}
                      </Text>
                    </View>

                    <TouchableOpacity
                      style={[
                        styles.checkButton,
                        completed && styles.checkButtonActive
                      ]}
                      onPress={() => {
                        if (completed) {
                          uncompleteMutation.mutate(habit.id);
                        } else {
                          completeMutation.mutate(habit.id);
                        }
                      }}
                    >
                      <Text style={styles.checkIcon}>
                        {completed ? '✓' : ''}
                      </Text>
                    </TouchableOpacity>
                  </View>
                </Card>
              );
            })
          ) : (
            <Card style={styles.emptyCard}>
              <Text style={styles.emptyEmoji}>🎯</Text>
              <Text style={styles.emptyText}>
                No habits yet. Create your first habit to get started!
              </Text>
            </Card>
          )}
        </View>
      </ScrollView>

      {/* Create Habit Modal */}
      <Modal
        visible={showModal}
        animationType="slide"
        transparent
        onRequestClose={() => setShowModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Create New Habit</Text>

            <TextInput
              style={styles.input}
              placeholder="Habit title (e.g., Morning meditation)"
              placeholderTextColor={colors.gray}
              value={newHabit.title}
              onChangeText={(text) => setNewHabit({ ...newHabit, title: text })}
            />

            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Description (optional)"
              placeholderTextColor={colors.gray}
              multiline
              numberOfLines={3}
              value={newHabit.description}
              onChangeText={(text) => setNewHabit({ ...newHabit, description: text })}
            />

            <View style={styles.modalButtons}>
              <Button
                title="Cancel"
                onPress={() => setShowModal(false)}
                variant="outline"
                style={styles.modalButton}
              />
              <Button
                title="Create"
                onPress={() => createMutation.mutate()}
                loading={createMutation.isPending}
                disabled={!newHabit.title}
                style={styles.modalButton}
              />
            </View>
          </View>
        </View>
      </Modal>
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
  createButton: {
    marginBottom: spacing.md
  },
  habitCard: {
    marginBottom: spacing.sm
  },
  habitHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  habitInfo: {
    flex: 1,
    marginRight: spacing.md
  },
  habitTitle: {
    ...typography.h3,
    marginBottom: spacing.xs
  },
  habitDescription: {
    ...typography.bodySmall,
    color: colors.gray,
    marginBottom: spacing.xs
  },
  habitStreak: {
    ...typography.caption,
    color: colors.softBlue
  },
  checkButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    borderWidth: 3,
    borderColor: colors.lightGray,
    alignItems: 'center',
    justifyContent: 'center'
  },
  checkButtonActive: {
    backgroundColor: colors.success,
    borderColor: colors.success
  },
  checkIcon: {
    fontSize: 24,
    color: colors.white,
    fontWeight: '700'
  },
  emptyCard: {
    alignItems: 'center',
    padding: spacing.xl
  },
  emptyEmoji: {
    fontSize: 64,
    marginBottom: spacing.md
  },
  emptyText: {
    ...typography.body,
    color: colors.gray,
    textAlign: 'center'
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    padding: spacing.lg
  },
  modalContent: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.xl,
    padding: spacing.xl
  },
  modalTitle: {
    ...typography.h2,
    marginBottom: spacing.lg
  },
  input: {
    backgroundColor: colors.offWhite,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    fontSize: 16,
    marginBottom: spacing.md
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top'
  },
  modalButtons: {
    flexDirection: 'row',
    gap: spacing.md,
    marginTop: spacing.md
  },
  modalButton: {
    flex: 1
  }
});
