/**
 * Reusable Card component
 */
import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { colors, borderRadius, spacing, shadows } from '../../utils/theme';

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  padding?: number;
  gradient?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  style,
  padding = spacing.md,
  gradient = false
}) => {
  return (
    <View style={[styles.card, { padding }, style]}>
      {children}
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.lg,
    ...shadows.medium
  }
});
