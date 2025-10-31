import { ReactNode } from "react";
import {
 Table,
 TableBody,
 TableCell,
 TableHead,
 TableHeader,
 TableRow,
} from "@/components/ui/table";
import { theme } from "@/lib/theme";
import { AlertCircle } from "lucide-react";

interface DataTableProps {
 children: ReactNode;
 className?: string;
}

interface DataTableEmptyProps {
 title?: string;
 description?: string;
 icon?: ReactNode;
}

export function DataTable({ children, className = "" }: DataTableProps) {
 return (
 <div className={`${theme.table.container} ${className}`}>
 {children}
 </div>
 );
}

export function DataTableEmpty({
  title = "No data found",
  description,
  icon,
}: DataTableEmptyProps) {
  return (
    <div className="text-center py-16 px-4">
      {icon || (
        <AlertCircle className="h-10 w-10 mx-auto mb-4 text-zinc-500 stroke-[1.5]" />
      )}
      <p className="text-sm font-semibold text-foreground-h2 mb-1">{title}</p>
      {description && (
        <p className="text-sm text-muted-foreground max-w-md mx-auto">{description}</p>
      )}
    </div>
  );
}

export { Table, TableBody, TableCell, TableHead, TableHeader, TableRow };
