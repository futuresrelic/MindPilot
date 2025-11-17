/**
 * Paywall / Subscription Screen
 */
import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Linking
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useQuery } from '@tanstack/react-query';
import { LinearGradient } from 'expo-linear-gradient';
import { subscriptionAPI } from '../utils/api';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { colors, spacing, typography, borderRadius } from '../utils/theme';

const FEATURES = [
  { icon: '✅', text: 'Unlimited habits tracking' },
  { icon: '✅', text: 'Unlimited AI journal reflections' },
  { icon: '✅', text: 'All premium audio content' },
  { icon: '✅', text: 'Advanced sleep analysis' },
  { icon: '✅', text: 'Weekly personalized reports' },
  { icon: '✅', text: 'Guided CBT sessions' },
  { icon: '✅', text: 'Priority support' },
  { icon: '✅', text: 'No limitations' }
];

const TESTIMONIALS = [
  {
    text: "MindPilot helped me build sustainable habits and understand my emotions better. The AI insights are incredible!",
    author: "Sarah K."
  },
  {
    text: "The best wellness app I've tried. It feels like having a supportive friend in my pocket.",
    author: "Michael T."
  },
  {
    text: "Premium is worth every penny. The weekly reports alone have transformed my self-awareness.",
    author: "Jessica L."
  }
];

export default function Paywall() {
  const router = useRouter();
  const [selectedPlan, setSelectedPlan] = useState<'monthly' | 'yearly'>('yearly');
  const [loading, setLoading] = useState(false);

  const { data: plans } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: async () => {
      const response = await subscriptionAPI.getPlans();
      return response.data;
    }
  });

  const handleSubscribe = async () => {
    if (!plans) return;

    const plan = plans.plans.find((p: any) => p.id === selectedPlan);
    if (!plan) return;

    setLoading(true);

    try {
      const response = await subscriptionAPI.createCheckout(
        plan.price_id,
        'mindpilot://payment-success',
        'mindpilot://payment-cancel'
      );

      // Open Stripe checkout
      await Linking.openURL(response.data.checkout_url);
    } catch (error) {
      console.error('Subscription error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView>
        <LinearGradient
          colors={['#6FA8FF', '#B8A2FF', '#FF9FB0']}
          style={styles.header}
        >
          <TouchableOpacity onPress={() => router.back()} style={styles.close}>
            <Text style={styles.closeText}>✕</Text>
          </TouchableOpacity>

          <Text style={styles.logo}>🧠✨</Text>
          <Text style={styles.title}>MindPilot+</Text>
          <Text style={styles.subtitle}>
            Unlock your full wellness potential
          </Text>
        </LinearGradient>

        <View style={styles.content}>
          {/* Features */}
          <Card>
            <Text style={styles.sectionTitle}>What you get:</Text>
            <View style={styles.features}>
              {FEATURES.map((feature, index) => (
                <View key={index} style={styles.feature}>
                  <Text style={styles.featureIcon}>{feature.icon}</Text>
                  <Text style={styles.featureText}>{feature.text}</Text>
                </View>
              ))}
            </View>
          </Card>

          {/* Plans */}
          {plans && (
            <View style={styles.plans}>
              {plans.plans.map((plan: any) => (
                <TouchableOpacity
                  key={plan.id}
                  style={[
                    styles.plan,
                    selectedPlan === plan.id && styles.planSelected
                  ]}
                  onPress={() => setSelectedPlan(plan.id)}
                >
                  {plan.savings && (
                    <View style={styles.savingsBadge}>
                      <Text style={styles.savingsText}>{plan.savings}</Text>
                    </View>
                  )}

                  <View style={styles.planHeader}>
                    <Text style={styles.planName}>{plan.name}</Text>
                    <View style={styles.planPrice}>
                      <Text style={styles.planAmount}>${plan.price}</Text>
                      <Text style={styles.planInterval}>/{plan.interval}</Text>
                    </View>
                  </View>

                  {selectedPlan === plan.id && (
                    <View style={styles.checkmark}>
                      <Text style={styles.checkmarkIcon}>✓</Text>
                    </View>
                  )}
                </TouchableOpacity>
              ))}

              <Text style={styles.trialInfo}>
                🎁 Start with a {plans.trial_days}-day free trial
              </Text>
            </View>
          )}

          <Button
            title="Start Free Trial"
            onPress={handleSubscribe}
            loading={loading}
            style={styles.subscribeButton}
          />

          {/* Testimonials */}
          <Text style={styles.sectionTitle}>What users say:</Text>
          {TESTIMONIALS.map((testimonial, index) => (
            <Card key={index} style={styles.testimonial}>
              <Text style={styles.testimonialText}>"{testimonial.text}"</Text>
              <Text style={styles.testimonialAuthor}>— {testimonial.author}</Text>
            </Card>
          ))}

          {/* Footer */}
          <Text style={styles.footer}>
            Cancel anytime. No commitments. Your data is always yours.
          </Text>
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
    paddingTop: spacing.xxl,
    paddingBottom: spacing.xxl * 1.5,
    alignItems: 'center'
  },
  close: {
    position: 'absolute',
    top: spacing.lg,
    right: spacing.lg,
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: 'rgba(255,255,255,0.3)',
    alignItems: 'center',
    justifyContent: 'center'
  },
  closeText: {
    color: colors.white,
    fontSize: 20,
    fontWeight: '700'
  },
  logo: {
    fontSize: 64,
    marginBottom: spacing.md
  },
  title: {
    ...typography.h1,
    color: colors.white,
    marginBottom: spacing.xs
  },
  subtitle: {
    ...typography.body,
    color: colors.white,
    opacity: 0.95
  },
  content: {
    padding: spacing.md,
    gap: spacing.md
  },
  sectionTitle: {
    ...typography.h3,
    marginBottom: spacing.md,
    marginTop: spacing.md
  },
  features: {
    gap: spacing.md
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md
  },
  featureIcon: {
    fontSize: 20
  },
  featureText: {
    ...typography.body,
    color: colors.darkGray,
    flex: 1
  },
  plans: {
    gap: spacing.md
  },
  plan: {
    backgroundColor: colors.white,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    borderWidth: 3,
    borderColor: colors.lightGray,
    position: 'relative'
  },
  planSelected: {
    borderColor: colors.softBlue,
    backgroundColor: '#F0F9FF'
  },
  savingsBadge: {
    position: 'absolute',
    top: -12,
    right: spacing.lg,
    backgroundColor: colors.success,
    paddingVertical: 4,
    paddingHorizontal: 12,
    borderRadius: 12
  },
  savingsText: {
    color: colors.white,
    fontSize: 12,
    fontWeight: '700'
  },
  planHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  planName: {
    ...typography.h3,
    flex: 1
  },
  planPrice: {
    alignItems: 'flex-end'
  },
  planAmount: {
    ...typography.h2,
    color: colors.softBlue
  },
  planInterval: {
    ...typography.bodySmall,
    color: colors.gray
  },
  checkmark: {
    position: 'absolute',
    top: spacing.md,
    right: spacing.md,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.softBlue,
    alignItems: 'center',
    justifyContent: 'center'
  },
  checkmarkIcon: {
    color: colors.white,
    fontSize: 14,
    fontWeight: '700'
  },
  trialInfo: {
    ...typography.body,
    color: colors.success,
    textAlign: 'center',
    fontWeight: '600'
  },
  subscribeButton: {
    marginVertical: spacing.md
  },
  testimonial: {
    backgroundColor: '#FFF9F0',
    marginBottom: spacing.sm
  },
  testimonialText: {
    ...typography.body,
    color: colors.darkGray,
    fontStyle: 'italic',
    marginBottom: spacing.sm
  },
  testimonialAuthor: {
    ...typography.bodySmall,
    color: colors.gray,
    fontWeight: '600'
  },
  footer: {
    ...typography.bodySmall,
    color: colors.gray,
    textAlign: 'center',
    marginTop: spacing.lg,
    marginBottom: spacing.xl
  }
});
