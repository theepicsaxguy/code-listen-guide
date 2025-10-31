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

 const borderStyles = {
 free: 'border-primary/30',
 professional: 'border-primary/50',
 team: 'border-accent/50',
 enterprise: 'border-warning/50'
 } as const;

 return (
 <span className={`inline-flex items-center px-3 py-1.5 rounded-full text-xs font-bold border-2 shadow-md ${styles[plan]} ${borderStyles[plan]}`}>
 {labels[plan]}
 </span>
 );
};
