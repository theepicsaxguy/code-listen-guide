import React from 'react';
import type { User } from '../../../lib/types';

interface PlanBadgeProps {
  plan: User['subscription_tier'];
}

export const PlanBadge: React.FC<PlanBadgeProps> = ({ plan }) => {
  const styles = {
    free: 'bg-muted/50 text-muted-foreground',
    professional: 'bg-primary/20 text-primary border-primary/30',
    team: 'bg-accent/20 text-accent border-accent/30',
    enterprise: 'bg-warning/20 text-warning border-warning/30'
  } as const;

  const labels = {
    free: 'Free',
    professional: 'Pro',
    team: 'Team',
    enterprise: 'Enterprise'
  } as const;

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${styles[plan]}`}>
      {labels[plan]}
    </span>
  );
};
