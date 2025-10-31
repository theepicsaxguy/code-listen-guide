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
 <span className="inline-flex items-center gap-1.5 rounded-full bg-green-500/5 px-2.5 py-1 text-xs font-medium uppercase tracking-wide text-green-300">
 <CheckCircle className="h-3 w-3 stroke-[1.5] text-green-300" />
 Completed
 </span>
 );
 }

 if (status === 'failed') {
 return (
 <span className="inline-flex items-center gap-1.5 rounded-full bg-red-500/5 px-2.5 py-1 text-xs font-medium uppercase tracking-wide text-red-300">
 <XCircle className="h-3 w-3 stroke-[1.5] text-red-300" />
 Failed
 </span>
 );
 }

 if (status === 'pending') {
 return (
 <span className="inline-flex items-center gap-1.5 rounded-full bg-purple-500/5 px-2.5 py-1 text-xs font-medium uppercase tracking-wide text-purple-300">
 <Loader className="h-3 w-3 animate-spin stroke-[1.5] text-purple-300" />
 Pending
 </span>
 );
 }

 return (
 <span className="inline-flex items-center gap-1.5 rounded-full bg-cyan-500/5 px-2.5 py-1 text-xs font-medium uppercase tracking-wide text-cyan-300">
 <Loader className="h-3 w-3 animate-spin stroke-[1.5] text-cyan-300" />
 {normalized.charAt(0).toUpperCase() + normalized.slice(1)}
 </span>
 );
};
