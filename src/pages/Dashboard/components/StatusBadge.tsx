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
 <span className="inline-flex items-center gap-1.5 rounded-md bg-success/10 px-2.5 py-1 text-caption font-semibold text-success shadow-sm">
 <CheckCircle className="h-3 w-3" />
 Completed
 </span>
 );
 }

 if (status === 'failed') {
 return (
 <span className="inline-flex items-center gap-1.5 rounded-md bg-danger/10 px-2.5 py-1 text-caption font-semibold text-danger shadow-sm">
 <XCircle className="h-3 w-3" />
 Failed
 </span>
 );
 }

 if (status === 'pending') {
 return (
 <span className="inline-flex items-center gap-1.5 rounded-md bg-surface-tertiary px-2.5 py-1 text-caption font-semibold text-muted-foreground shadow-sm">
 <Loader className="h-3 w-3 animate-spin" />
 Pending
 </span>
 );
 }

 return (
 <span className="inline-flex items-center gap-1.5 rounded-md bg-primary/10 px-2.5 py-1 text-caption font-semibold text-primary shadow-sm">
 <Loader className="h-3 w-3 animate-spin" />
 {normalized.charAt(0).toUpperCase() + normalized.slice(1)}
 </span>
 );
};
