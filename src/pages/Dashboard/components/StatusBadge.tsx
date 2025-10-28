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
          style: 'bg-green-500/20 text-green-400 border-green-500/30',
          icon: <CheckCircle size={12} />,
          label: 'Completed'
        };
      case 'failed':
        return {
          style: 'bg-red-500/20 text-red-400 border-red-500/30',
          icon: <XCircle size={12} />,
          label: 'Failed'
        };
      default: // pending, analyzing, scripting, synthesizing, post_processing
        return {
          style: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
          icon: <Loader size={12} className="animate-spin" />,
          label: status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')
        };
    }
  };

  const config = getStatusConfig();

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${config.style}`}>
      {config.icon}
      {config.label}
    </span>
  );
};
