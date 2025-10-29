import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function AdminContent() {
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery({
    queryKey: ["admin-jobs", statusFilter, page],
    queryFn: () => apiClient.request(`/admin/jobs?page=${page}${statusFilter ? `&status=${statusFilter}` : ""}`),
  });

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      completed: "bg-green-500/10 text-green-500",
      failed: "bg-red-500/10 text-red-500",
      pending: "bg-yellow-500/10 text-yellow-500",
      analyzing: "bg-blue-500/10 text-blue-500",
      scripting: "bg-purple-500/10 text-purple-500",
      synthesizing: "bg-pink-500/10 text-pink-500",
    };
    return colors[status] || "bg-gray-500/10 text-gray-500";
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Content Management</h1>
        <p className="text-gray-400 mt-1">
          Manage audiobooks and monitor job progress
        </p>
      </div>

      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="p-6 space-y-4">
          <div className="flex gap-4">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="analyzing">Analyzing</SelectItem>
                <SelectItem value="scripting">Scripting</SelectItem>
                <SelectItem value="synthesizing">Synthesizing</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {isLoading ? (
            <p className="text-center text-gray-400 py-8">Loading content...</p>
          ) : data?.jobs?.length === 0 ? (
            <div className="text-center text-gray-400 py-8">
              <p>No jobs found</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Job ID</TableHead>
                  <TableHead>Repository</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead>Created</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.jobs?.map((job: any) => (
                  <TableRow key={job.id}>
                    <TableCell className="font-mono text-xs">{job.id.slice(0, 8)}</TableCell>
                    <TableCell>
                      <a href={job.repo_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">
                        {job.repo_name}
                      </a>
                    </TableCell>
                    <TableCell className="font-mono text-xs">{job.user_id.slice(0, 8)}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(job.status)}>{job.status}</Badge>
                    </TableCell>
                    <TableCell>{job.progress_percentage}%</TableCell>
                    <TableCell>{new Date(job.created_at).toLocaleDateString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          <div className="flex justify-between items-center pt-4">
            <Button
              variant="outline"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="border-gray-700 hover:bg-gray-800"
            >
              Previous
            </Button>
            <span className="text-sm text-gray-400">Page {page}</span>
            <Button
              variant="outline"
              onClick={() => setPage(p => p + 1)}
              disabled={!data?.jobs || data.jobs.length < 20}
              className="border-gray-700 hover:bg-gray-800"
            >
              Next
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
