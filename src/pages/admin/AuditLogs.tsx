import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
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
  const { data, isLoading } = useQuery({
    queryKey: ["audit-logs"],
    queryFn: () => apiClient.request("/admin/audit-logs"),
  });

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Audit Logs</h1>
        <p className="text-gray-400 mt-1">
          View all admin actions and system events
        </p>
      </div>
      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="p-6">
          {isLoading ? (
            <p className="text-center text-gray-400">Loading audit logs...</p>
          ) : data?.logs?.length === 0 ? (
            <div className="text-center text-gray-400">
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
