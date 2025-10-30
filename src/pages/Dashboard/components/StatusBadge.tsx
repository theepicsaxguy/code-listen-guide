import React from 'react';
import { Loader, CheckCircle, XCircle } from 'lucide-react';
import type { Job } from '../../../lib/types';

interface StatusBadgeProps {
  status: Job['status'];
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'completed':
        return {
          style: 'bg-success/10 text-success border-success/30',
          icon: <CheckCircle size={12} />,
          label: 'Completed'
        };
      case 'failed':
        return {
          style: 'bg-destructive/10 text-destructive border-destructive/30',
          icon: <XCircle size={12} />,
          label: 'Failed'
        };
      default: // pending, analyzing, scripting, synthesizing, post_processing
        return {
          style: 'bg-primary/10 text-primary border-primary/30',
          icon: <Loader size={12} className="animate-spin" />,
          label: status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')
        };
    }
  };

  const config = getStatusConfig();

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${config.style} shadow-sm`}>
      {config.icon}
      {config.label}
    </span>
  );
};
