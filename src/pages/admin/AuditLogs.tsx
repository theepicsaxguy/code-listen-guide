import { useGetAuditLogs } from "@/lib/api/generated";
import { Card, CardContent } from "@/components/ui/card";
import {
 Table,
 TableBody,
 TableCell,
 TableHead,
 TableHeader,
 TableRow,
} from "@/components/ui/table";

export default function AdminAuditLogs() {
 const { data, isLoading } = useGetAuditLogs();

 return (
 <div className="p-8 space-y-6">
 <div>
 <h1 className="text-3xl font-bold text-foreground">Audit Logs</h1>
 <p className="text-muted-foreground mt-1">
 View all admin actions and system events
 </p>
 </div>
 <Card className="bg-card">
 <CardContent className="p-6">
 {isLoading ? (
 <p className="text-center text-muted-foreground">Loading audit logs...</p>
 ) : data?.logs?.length === 0 ? (
 <div className="text-center text-muted-foreground">
 <p>No audit logs found</p>
 <p className="text-sm mt-2">Admin actions will be logged here</p>
 </div>
 ) : (
 <Table>
 <TableHeader>
 <TableRow>
 <TableHead>Timestamp</TableHead>
 <TableHead>Admin</TableHead>
 <TableHead>Action</TableHead>
 <TableHead>Details</TableHead>
 </TableRow>
 </TableHeader>
 <TableBody>
 {data?.logs?.map((log: any) => (
 <TableRow key={log.id}>
 <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
 <TableCell>{log.admin_email}</TableCell>
 <TableCell>{log.action}</TableCell>
 <TableCell>{log.details}</TableCell>
 </TableRow>
 ))}
 </TableBody>
 </Table>
 )}
 </CardContent>
 </Card>
 </div>
 );
}
