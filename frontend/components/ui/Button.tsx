/**
 * Reusable Button component
 */
import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle, TextStyle } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { colors, borderRadius, spacing, typography, shadows } from '../../utils/theme';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  style,
  textStyle,
  icon
}) => {
  const getButtonContent = () => (
    <TouchableOpacity
      style={[
        styles.button,
        styles[`button_${size}`],
        variant !== 'primary' && styles[`button_${variant}`],
        disabled && styles.disabled,
        style
      ]}
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
    >
      {loading ? (
        <ActivityIndicator color={variant === 'primary' ? colors.white : colors.softBlue} />
      ) : (
        <>
          {icon}
          <Text
            style={[
              styles.text,
              styles[`text_${size}`],
              variant !== 'primary' && styles[`text_${variant}`],
              disabled && styles.textDisabled,
              textStyle
            ]}
          >
            {title}
          </Text>
        </>
      )}
    </TouchableOpacity>
  );

  if (variant === 'primary' && !disabled) {
    return (
      <LinearGradient
        colors={['#6FA8FF', '#B8A2FF']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
        style={[styles.gradient, style]}
      >
        {getButtonContent()}
      </LinearGradient>
    );
  }

  return getButtonContent();
};

const styles = StyleSheet.create({
  gradient: {
    borderRadius: borderRadius.md,
    ...shadows.small
  },
  button: {
    borderRadius: borderRadius.md,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    gap: spacing.sm
  },
  button_small: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md
  },
  button_medium: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg
  },
  button_large: {
    paddingVertical: spacing.lg,
    paddingHorizontal: spacing.xl
  },
  button_secondary: {
    backgroundColor: colors.lightGray
  },
  button_outline: {
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: colors.softBlue
  },
  button_ghost: {
    backgroundColor: 'transparent'
  },
  disabled: {
    opacity: 0.5
  },
  text: {
    fontWeight: '600',
    color: colors.white
  },
  text_small: {
    fontSize: 14
  },
  text_medium: {
    fontSize: 16
  },
  text_large: {
    fontSize: 18
  },
  text_secondary: {
    color: colors.darkGray
  },
  text_outline: {
    color: colors.softBlue
  },
  text_ghost: {
    color: colors.softBlue
  },
  textDisabled: {
    color: colors.gray
  }
});
