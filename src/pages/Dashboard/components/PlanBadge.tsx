import React from 'react';
import type { User } from '../../../lib/types';

interface PlanBadgeProps {
  plan: User['subscription_tier'];
}

export const PlanBadge: React.FC<PlanBadgeProps> = ({ plan }) => {
  const styles = {
    free: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    professional: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    team: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    enterprise: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
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
