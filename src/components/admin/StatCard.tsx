import { LucideIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

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

/**
 * Unified StatCard component using token-based styling.
 * Replaces hardcoded grays with semantic tokens from the theme.
 */
export const StatCard = ({ title, value, icon: Icon, description, trend }: StatCardProps) => {
  return (
    <Card className="bg-gradient-stat border border-border/50 shadow-sm hover:shadow-lg transition-all duration-300 group relative overflow-hidden hover-card card-elevation">
      <div className="absolute inset-0 bg-gradient-primary opacity-0 group-hover:opacity-5 transition-opacity" />
      <CardHeader className="flex flex-row items-center justify-between pb-3 space-y-0 relative z-10">
        <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">{title}</CardTitle>
        <div className="w-10 h-10 rounded-xl bg-gradient-primary/20 flex items-center justify-center shadow-md shadow-primary/10">
          <Icon className="h-5 w-5 icon-gradient" />
        </div>
      </CardHeader>
      <CardContent className="relative z-10">
        <div className="text-4xl font-bold text-foreground mb-1">{value}</div>
        {description && <p className="text-xs text-muted-foreground mt-2 font-medium">{description}</p>}
        {trend && (
          <div
            className={`text-xs mt-3 flex items-center gap-1.5 font-semibold px-2.5 py-1 rounded-full w-fit ${
              trend.isPositive 
                ? "text-success bg-success/10" 
                : "text-destructive bg-destructive/10"
            }`}
          >
            <span>{trend.isPositive ? "↑" : "↓"}</span>
            <span>{Math.abs(trend.value)}% from last period</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
