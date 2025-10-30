import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import type { AdminUser } from "@/types/admin";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { Plus, Minus, History, CreditCard, Settings } from "lucide-react";

interface ExtendedAdminUser extends AdminUser {
  subscription_tier?: string;
}

interface UserJobsResponse {
  jobs: Array<{
    id: string;
    repo_url: string;
    repo_name: string;
    status: string;
    depth_tier: string;
    price_paid_cents: number;
    created_at: string;
  }>;
}

interface UserDetailsDialogProps {
  userId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function UserDetailsDialog({ userId, isOpen, onClose }: UserDetailsDialogProps) {
  const [creditAmount, setCreditAmount] = useState("");
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery<ExtendedAdminUser>({
    queryKey: ["admin-user", userId],
    queryFn: () => apiClient.getUser(userId) as Promise<ExtendedAdminUser>,
    enabled: isOpen && Boolean(userId),
  });

  const { data: userJobs } = useQuery<UserJobsResponse>({
    queryKey: ["admin-user-jobs", userId],
    queryFn: () => apiClient.getUserJobs(userId),
    enabled: isOpen && Boolean(userId),
  });

  const creditMutation = useMutation({
    mutationFn: ({ amount, operation }: { amount: number; operation: "add" | "subtract" }) =>
      apiClient.request(`/admin/users/${userId}/credits`, {
        method: "POST",
        body: JSON.stringify({ amount, operation }),
      }),
    onSuccess: () => {
      toast.success("Credits updated successfully");
      setCreditAmount("");
      queryClient.invalidateQueries({ queryKey: ["admin-user", userId] });
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
    },
    onError: () => toast.error("Failed to update credits"),
  });

  const handleAddCredits = () => {
    const amount = parseInt(creditAmount);
    if (!amount || amount <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }
    creditMutation.mutate({ amount, operation: "add" });
  };

  const handleRemoveCredits = () => {
    const amount = parseInt(creditAmount);
    if (!amount || amount <= 0) {
      toast.error("Please enter a valid amount");
      return;
    }
    creditMutation.mutate({ amount, operation: "subtract" });
  };

  if (isLoading) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  if (!user) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">User Details</DialogTitle>
          <DialogDescription>
            Manage user information, credits, and view activity
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* User Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Account Information
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-muted-foreground">Name</Label>
                <p className="font-medium">{user.name}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Email</Label>
                <p className="font-medium">{user.email}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Status</Label>
                <div className="mt-1">
                  <Badge variant={user.status === "active" ? "default" : "destructive"}>
                    {user.status}
                  </Badge>
                </div>
              </div>
              <div>
                <Label className="text-muted-foreground">Subscription</Label>
                <div className="mt-1">
                  <Badge variant="outline" className="capitalize">
                    {user.subscription_tier || "free"}
                  </Badge>
                </div>
              </div>
              <div>
                <Label className="text-muted-foreground">Joined</Label>
                <p className="text-sm">{new Date(user.created_at).toLocaleDateString()}</p>
              </div>
              <div>
                <Label className="text-muted-foreground">Last Login</Label>
                <p className="text-sm">
                  {user.last_login ? new Date(user.last_login).toLocaleDateString() : "Never"}
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Credits Management */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Credits Management
              </CardTitle>
              <CardDescription>
                Current balance: <span className="font-bold text-foreground">{user.credits}</span> credits
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-3">
                <Input
                  type="number"
                  placeholder="Amount"
                  value={creditAmount}
                  onChange={(e) => setCreditAmount(e.target.value)}
                  className="max-w-xs"
                  min="1"
                />
                <Button
                  onClick={handleAddCredits}
                  disabled={creditMutation.isPending}
                  variant="default"
                  className="gap-2"
                >
                  <Plus className="h-4 w-4" />
                  Add Credits
                </Button>
                <Button
                  onClick={handleRemoveCredits}
                  disabled={creditMutation.isPending}
                  variant="destructive"
                  className="gap-2"
                >
                  <Minus className="h-4 w-4" />
                  Remove Credits
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Job History */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" />
                Job History
              </CardTitle>
              <CardDescription>Recent audiobook generation requests</CardDescription>
            </CardHeader>
            <CardContent>
              {!userJobs?.jobs || userJobs.jobs.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">No jobs found</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Repository</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Tier</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead>Price</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {userJobs.jobs.map((job: any) => (
                      <TableRow key={job.id}>
                        <TableCell>
                          <div className="font-medium">{job.repo_name}</div>
                          <div className="text-xs text-muted-foreground">{job.repo_owner}</div>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant="outline"
                            className={
                              job.status === "completed"
                                ? "bg-green-500/10 text-green-500"
                                : job.status === "failed"
                                ? "bg-red-500/10 text-red-500"
                                : "bg-blue-500/10 text-blue-500"
                            }
                          >
                            {job.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="capitalize">{job.depth_tier}</TableCell>
                        <TableCell>{new Date(job.created_at).toLocaleDateString()}</TableCell>
                        <TableCell>${(job.price_paid_cents / 100).toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
