import { useEffect, useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { apiClient } from "@/lib/api";
import { Payment, PaymentDetails, PaymentStats } from "@/types/admin";
import { toast } from "sonner";
import {
  DollarSign,
  TrendingUp,
  CreditCard,
  Activity,
  Search,
  Download,
  RefreshCw,
  Eye,
  Ban,
} from "lucide-react";

export default function AdminPayments() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [stats, setStats] = useState<PaymentStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [selectedPayment, setSelectedPayment] = useState<PaymentDetails | null>(null);
  const [showRefundDialog, setShowRefundDialog] = useState(false);
  const [refundAmount, setRefundAmount] = useState("");
  const [refundReason, setRefundReason] = useState("requested_by_customer");
  const [isRefunding, setIsRefunding] = useState(false);

  useEffect(() => {
    void fetchStats();
  }, []);

  useEffect(() => {
    void fetchPayments();
  }, [page, statusFilter]);

  const fetchStats = async () => {
    try {
      const data = await apiClient.getPaymentStats();
      setStats(data);
    } catch (error) {
      console.error("Failed to load payment stats:", error);
    }
  };

  const fetchPayments = async () => {
    setIsLoading(true);
    try {
      const data = searchQuery
        ? await apiClient.searchPayments({
            page,
            query: searchQuery,
            status: statusFilter || undefined,
          })
        : await apiClient.getPayments(page);
      
      setPayments(data.payments || []);
      setTotalPages(Math.ceil((data.total || 0) / 20));
    } catch (error) {
      toast.error("Failed to load payments");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    void fetchPayments();
  };

  const handleViewDetails = async (paymentId: string) => {
    try {
      const details = await apiClient.getPaymentDetails(paymentId);
      setSelectedPayment(details);
    } catch (error) {
      toast.error("Failed to load payment details");
      console.error(error);
    }
  };

  const handleRefund = async () => {
    if (!selectedPayment) return;
    
    setIsRefunding(true);
    try {
      const refundData: { amount?: number; reason: string } = {
        reason: refundReason,
      };
      
      if (refundAmount) {
        refundData.amount = parseFloat(refundAmount);
      }

      const result = await apiClient.refundPayment(selectedPayment.id, refundData);
      
      toast.success(`Refund successful! Amount: $${result.amount_refunded.toFixed(2)}`);
      setShowRefundDialog(false);
      setSelectedPayment(null);
      setRefundAmount("");
      
      // Refresh data
      void fetchPayments();
      void fetchStats();
    } catch (error) {
      toast.error("Failed to process refund");
      console.error(error);
    } finally {
      setIsRefunding(false);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      toast.info(`Downloading ${format.toUpperCase()} export...`);
      await apiClient.exportPayments(format, {
        status: statusFilter || undefined,
      });
      toast.success("Export downloaded successfully");
    } catch (error) {
      toast.error("Failed to export payments");
      console.error(error);
    }
  };

  const getStatusColor = (status: Payment["status"]) => {
    switch (status) {
      case "succeeded":
        return "default" as const;
      case "pending":
        return "secondary" as const;
      case "failed":
        return "destructive" as const;
      case "refunded":
        return "outline" as const;
      default:
        return "secondary" as const;
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount);
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Payment Management</h1>
          <p className="text-muted-foreground mt-1">View and manage all payment transactions</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => handleExport('csv')}>
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline" onClick={() => handleExport('json')}>
            <Download className="h-4 w-4 mr-2" />
            Export JSON
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.total_revenue.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">All time</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">This Month</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.revenue_this_month.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">
                {stats.revenue_last_month > 0
                  ? `${((stats.revenue_this_month / stats.revenue_last_month - 1) * 100).toFixed(1)}% from last month`
                  : 'First month'}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Payments</CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_payments}</div>
              <p className="text-xs text-muted-foreground">
                {stats.status_counts.succeeded || 0} succeeded
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Transaction</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.average_transaction.toFixed(2)}</div>
              <p className="text-xs text-muted-foreground">
                {stats.recent_transaction_count} in last 7 days
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Search Payments</CardTitle>
          <CardDescription>Filter by status, user, or Stripe ID</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search by payment intent ID, charge ID, or user email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
          </div>
          <Select value={statusFilter || "all"} onValueChange={(value) => setStatusFilter(value === "all" ? "" : value)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="All statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All statuses</SelectItem>
              <SelectItem value="succeeded">Succeeded</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
              <SelectItem value="refunded">Refunded</SelectItem>
            </SelectContent>
          </Select>
          <Button onClick={handleSearch}>
            <Search className="h-4 w-4 mr-2" />
            Search
          </Button>
          <Button variant="outline" onClick={() => {
            setSearchQuery("");
            setStatusFilter("");
            setPage(1);
            void fetchPayments();
          }}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset
          </Button>
        </CardContent>
      </Card>

      {/* Payments Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Payment Method</TableHead>
              <TableHead>Job ID</TableHead>
              <TableHead>Date</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8">
                  Loading payments...
                </TableCell>
              </TableRow>
            ) : payments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                  No payments found
                </TableCell>
              </TableRow>
            ) : (
              payments.map((payment) => (
                <TableRow key={payment.id}>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-medium">{payment.user_email}</span>
                      <span className="text-xs text-muted-foreground font-mono">
                        {payment.user_id.substring(0, 8)}...
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="font-semibold">
                    {formatCurrency(payment.amount, payment.currency)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStatusColor(payment.status)}>{payment.status}</Badge>
                  </TableCell>
                  <TableCell>{payment.payment_method || "—"}</TableCell>
                  <TableCell className="font-mono text-xs">
                    {payment.job_id ? payment.job_id.substring(0, 8) + "..." : "—"}
                  </TableCell>
                  <TableCell className="text-sm">
                    {new Date(payment.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewDetails(payment.id)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {payment.status === "succeeded" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            void handleViewDetails(payment.id);
                            setShowRefundDialog(true);
                          }}
                        >
                          <Ban className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Pagination */}
      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          onClick={() => setPage((value) => Math.max(1, value - 1))}
          disabled={page === 1}
        >
          Previous
        </Button>
        <span className="text-sm text-muted-foreground">
          Page {page} of {totalPages}
        </span>
        <Button
          variant="outline"
          onClick={() => setPage((value) => value + 1)}
          disabled={page >= totalPages}
        >
          Next
        </Button>
      </div>

      {/* Payment Details Dialog */}
      <Dialog open={!!selectedPayment && !showRefundDialog} onOpenChange={(open) => !open && setSelectedPayment(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Payment Details</DialogTitle>
            <DialogDescription>Complete payment transaction information</DialogDescription>
          </DialogHeader>
          {selectedPayment && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Payment ID</label>
                  <p className="font-mono text-sm">{selectedPayment.id}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Status</label>
                  <div className="mt-1">
                    <Badge variant={getStatusColor(selectedPayment.status)}>
                      {selectedPayment.status}
                    </Badge>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">User</label>
                  <p>{selectedPayment.user.email}</p>
                  <p className="text-sm text-muted-foreground">{selectedPayment.user.name}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Amount</label>
                  <p className="text-lg font-semibold">
                    {formatCurrency(selectedPayment.amount, selectedPayment.currency)}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Payment Method</label>
                  <p>{selectedPayment.payment_method_type || "—"}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Created</label>
                  <p>{new Date(selectedPayment.created_at).toLocaleString()}</p>
                </div>
                {selectedPayment.stripe_payment_intent_id && (
                  <div className="col-span-2">
                    <label className="text-sm font-medium text-muted-foreground">
                      Stripe Payment Intent
                    </label>
                    <p className="font-mono text-sm">{selectedPayment.stripe_payment_intent_id}</p>
                  </div>
                )}
                {selectedPayment.job && (
                  <div className="col-span-2">
                    <label className="text-sm font-medium text-muted-foreground">
                      Associated Job
                    </label>
                    <div className="mt-2 p-4 bg-muted rounded-lg">
                      <p className="font-medium">{selectedPayment.job.repo_name}</p>
                      <p className="text-sm text-muted-foreground">{selectedPayment.job.repo_url}</p>
                      <div className="flex gap-2 mt-2">
                        <Badge>{selectedPayment.job.depth_tier}</Badge>
                        <Badge variant="outline">{selectedPayment.job.status}</Badge>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
          <DialogFooter>
            {selectedPayment?.status === "succeeded" && (
              <Button
                variant="destructive"
                onClick={() => setShowRefundDialog(true)}
              >
                Issue Refund
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Refund Dialog */}
      <Dialog open={showRefundDialog} onOpenChange={setShowRefundDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Issue Refund</DialogTitle>
            <DialogDescription>
              Process a refund for this payment through Stripe
            </DialogDescription>
          </DialogHeader>
          {selectedPayment && (
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Payment Amount</p>
                <p className="text-lg font-semibold">
                  {formatCurrency(selectedPayment.amount, selectedPayment.currency)}
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">Refund Amount (optional)</label>
                <Input
                  type="number"
                  placeholder="Leave empty for full refund"
                  value={refundAmount}
                  onChange={(e) => setRefundAmount(e.target.value)}
                  step="0.01"
                  max={selectedPayment.amount}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Leave empty to refund the full amount
                </p>
              </div>
              <div>
                <label className="text-sm font-medium">Reason</label>
                <Select value={refundReason} onValueChange={setRefundReason}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="z-[9999]">
                    <SelectItem value="requested_by_customer">Requested by Customer</SelectItem>
                    <SelectItem value="duplicate">Duplicate</SelectItem>
                    <SelectItem value="fraudulent">Fraudulent</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowRefundDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleRefund}
              disabled={isRefunding}
            >
              {isRefunding ? "Processing..." : "Confirm Refund"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
