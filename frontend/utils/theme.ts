/**
 * Design system and theme
 */

export const colors = {
  // Primary palette
  softBlue: '#6FA8FF',
  calmPink: '#FF9FB0',
  lavender: '#B8A2FF',
  aqua: '#74E4D4',
  midnight: '#0A0F2B',

  // Neutrals
  white: '#FFFFFF',
  offWhite: '#F8F9FA',
  lightGray: '#E5E7EB',
  gray: '#9CA3AF',
  darkGray: '#4B5563',
  black: '#1F2937',

  // Semantic
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',

  // Mood colors
  mood: {
    veryLow: '#EF4444',
    low: '#F59E0B',
    medium: '#F59E0B',
    good: '#10B981',
    great: '#6FA8FF'
  }
};

export const gradients = {
  primary: ['#6FA8FF', '#B8A2FF'],
  calm: ['#74E4D4', '#6FA8FF'],
  warm: ['#FF9FB0', '#B8A2FF'],
  sunrise: ['#F59E0B', '#FF9FB0'],
  midnight: ['#0A0F2B', '#4B5563']
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48
};

export const borderRadius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
  full: 9999
};

export const typography = {
  h1: {
    fontSize: 32,
    fontWeight: '700' as const,
    lineHeight: 40
  },
  h2: {
    fontSize: 24,
    fontWeight: '600' as const,
    lineHeight: 32
  },
  h3: {
    fontSize: 20,
    fontWeight: '600' as const,
    lineHeight: 28
  },
  body: {
    fontSize: 16,
    fontWeight: '400' as const,
    lineHeight: 24
  },
  bodySmall: {
    fontSize: 14,
    fontWeight: '400' as const,
    lineHeight: 20
  },
  caption: {
    fontSize: 12,
    fontWeight: '400' as const,
    lineHeight: 16
  }
};

export const shadows = {
  small: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2
  },
  medium: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4
  },
  large: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.15,
    shadowRadius: 16,
    elevation: 8
  }
};

export const getMoodColor = (moodValue: number): string => {
  if (moodValue <= 2) return colors.mood.veryLow;
  if (moodValue <= 4) return colors.mood.low;
  if (moodValue <= 6) return colors.mood.medium;
  if (moodValue <= 8) return colors.mood.good;
  return colors.mood.great;
};

export const getMoodEmoji = (moodValue: number): string => {
  if (moodValue <= 2) return '😢';
  if (moodValue <= 4) return '😔';
  if (moodValue <= 6) return '😐';
  if (moodValue <= 8) return '🙂';
  return '😄';
};
