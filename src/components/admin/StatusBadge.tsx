import { Badge } from "@/components/ui/badge";
import { getStatusClasses } from "@/lib/theme";
import { CheckCircle2, XCircle, Clock, Loader2, AlertCircle } from "lucide-react";

interface StatusBadgeProps {
 status: string;
 showIcon?: boolean;
}

function getStatusIcon(status: string) {
 const normalized = status.toLowerCase();

 switch (normalized) {
 case "completed":
 case "success":
 case "active":
 return <CheckCircle2 className="h-3.5 w-3.5" />;

 case "failed":
 case "error":
 case "suspended":
 return <XCircle className="h-3.5 w-3.5" />;

 case "analyzing":
 case "scripting":
 case "synthesizing":
 case "post_processing":
 case "processing":
 case "running":
 return <Loader2 className="h-3.5 w-3.5 animate-spin" />;

 case "waiting_approval":
 case "warning":
 return <AlertCircle className="h-3.5 w-3.5" />;

 case "pending":
 case "queued":
 default:
 return <Clock className="h-3.5 w-3.5" />;
 }
}

export function StatusBadge({ status, showIcon = true }: StatusBadgeProps) {
 const classes = getStatusClasses(status);

 return (
 <Badge
 variant="outline"
 className={`${classes.bg} ${classes.text} ${classes.border}`}
 >
 <span className="flex items-center gap-1.5">
 {showIcon && getStatusIcon(status)}
 {status}
 </span>
 </Badge>
 );
}
