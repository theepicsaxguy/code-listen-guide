import { LucideIcon } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface StatCardProps {
 title: string;
 value: string | number;
 icon: LucideIcon;
 description?: string;
 trend?: {
 value: number;
 isPositive: boolean;
 };
}

export const StatCard = ({ title, value, icon: Icon, description, trend }: StatCardProps) => (
 <Card className="rounded-card bg-surface-secondary shadow-md hover:shadow-lg transition-standard">
 <CardHeader className="flex items-center justify-between">
 <div>
 <CardDescription className="text-caption uppercase tracking-wide text-muted-foreground">{title}</CardDescription>
 <CardTitle className="text-heading font-semibold text-foreground">{value}</CardTitle>
 </div>
 <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10 text-primary">
 <Icon className="h-5 w-5" />
 </div>
 </CardHeader>
 <CardContent className="space-y-3">
 {description && <p className="text-caption text-muted-foreground">{description}</p>}
 {trend && (
 <div
 className={`inline-flex items-center gap-1 rounded-md px-2.5 py-1 text-caption font-semibold ${
 trend.isPositive ? "bg-success/10 text-success" : "bg-danger/10 text-danger"
 }`}
 >
 <span>{trend.isPositive ? "▲" : "▼"}</span>
 <span>{Math.abs(trend.value)}% from last period</span>
 </div>
 )}
 </CardContent>
 </Card>
);
