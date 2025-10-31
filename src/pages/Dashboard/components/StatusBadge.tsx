import React from 'react';
import { Loader, CheckCircle, XCircle } from 'lucide-react';

import type { Job } from '../../../lib/types';

interface StatusBadgeProps {
 status: Job['status'];
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
 const normalized = status.replace('_', ' ');

 if (status === 'completed') {
 return (
 <span className="inline-flex items-center gap-1.5 rounded-control bg-success/5 px-2.5 py-1 text-xs font-semibold text-success">
 <CheckCircle className="h-3 w-3" />
 Completed
 </span>
 );
 }

 if (status === 'failed') {
 return (
 <span className="inline-flex items-center gap-1.5 rounded-control bg-danger/5 px-2.5 py-1 text-xs font-semibold text-danger">
 <XCircle className="h-3 w-3" />
 Failed
 </span>
 );
 }

 if (status === 'pending') {
 return (
 <span className="inline-flex items-center gap-1.5 rounded-control bg-pending/5 px-2.5 py-1 text-xs font-semibold text-pending">
 <Loader className="h-3 w-3 animate-spin" />
 Pending
 </span>
 );
 }

 return (
 <span className="inline-flex items-center gap-1.5 rounded-control bg-primary/5 px-2.5 py-1 text-xs font-semibold text-primary">
 <Loader className="h-3 w-3 animate-spin" />
 {normalized.charAt(0).toUpperCase() + normalized.slice(1)}
 </span>
 );
};
