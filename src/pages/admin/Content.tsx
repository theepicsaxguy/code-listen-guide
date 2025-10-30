import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import { Eye, Download, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function AdminContent() {
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const navigate = useNavigate();

  const { data, isLoading } = useQuery({
    queryKey: ["admin-jobs", statusFilter, page],
    queryFn: () => apiClient.getJobs(page, statusFilter === "all" ? undefined : statusFilter),
  });

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      completed: "bg-green-500/10 text-green-500 border-green-500/20",
      failed: "bg-red-500/10 text-red-500 border-red-500/20",
      pending: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
      analyzing: "bg-blue-500/10 text-blue-500 border-blue-500/20",
      scripting: "bg-purple-500/10 text-purple-500 border-purple-500/20",
      synthesizing: "bg-pink-500/10 text-pink-500 border-pink-500/20",
      waiting_approval: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    };
    return colors[status] || "bg-muted text-muted-foreground";
  };

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
          Content Management
        </h1>
        <p className="text-muted-foreground mt-1">
          Manage audiobook content and monitor generation progress
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="analyzing">Analyzing</SelectItem>
                <SelectItem value="waiting_approval">Waiting Approval</SelectItem>
                <SelectItem value="scripting">Scripting</SelectItem>
                <SelectItem value="synthesizing">Synthesizing</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {isLoading ? (
            <p className="text-center text-muted-foreground py-8">Loading content...</p>
          ) : !data?.jobs || data.jobs.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <p>No jobs found</p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Job ID</TableHead>
                    <TableHead>Repository</TableHead>
                    <TableHead>User</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Tier</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.jobs.map((job: any) => (
                    <TableRow key={job.id}>
                      <TableCell className="font-mono text-xs">{job.id.slice(0, 8)}</TableCell>
                      <TableCell>
                        <div>
                          <a href={job.repo_url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                            {job.repo_name}
                          </a>
                          <div className="text-xs text-muted-foreground">{job.repo_owner}</div>
                        </div>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{job.user_id.slice(0, 8)}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className={getStatusColor(job.status)}>
                          {job.status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{job.progress_percentage}%</span>
                          <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary transition-all"
                              style={{ width: `${job.progress_percentage}%` }}
                            />
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="capitalize">{job.depth_tier}</TableCell>
                      <TableCell>{new Date(job.created_at).toLocaleDateString()}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => navigate(`/admin/tracing?job=${job.id}`)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          {job.status === 'completed' && (
                            <Button size="sm" variant="ghost">
                              <Download className="h-4 w-4" />
                            </Button>
                          )}
                          <Button size="sm" variant="ghost" className="text-destructive">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}

          <div className="flex justify-between items-center pt-4">
            <Button
              variant="outline"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              Previous
            </Button>
            <span className="text-sm text-muted-foreground">Page {page}</span>
            <Button
              variant="outline"
              onClick={() => setPage(p => p + 1)}
              disabled={!data?.jobs || data.jobs.length < 20}
            >
              Next
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
