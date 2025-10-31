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
 <div className="text-center py-12 text-muted-foreground">
 {icon || <AlertCircle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />}
 <p className="font-semibold text-foreground">{title}</p>
 {description && <p className="text-sm mt-2 text-muted-foreground">{description}</p>}
 </div>
 );
}

export { Table, TableBody, TableCell, TableHead, TableHeader, TableRow };
