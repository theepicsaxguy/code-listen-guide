import { useState } from "react";
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
// Queries:
//  - useGetPaymentStats for stats cards
//  - useGetPayments (unfiltered list) and useSearchPayments (search results) with conditional enable flags
//  - useGetPaymentDetails for details dialog
// Mutations:
//  - useRefundPayment for issuing refunds (partial or full)
// Export:
//  - useExportPayments invoked via refetch with enabled:false (one-off download request)
// Notes:
//  - RefundRequest schema presently only includes `amount`; we optimistically pass a `reason` key (cast as any)
//    to preserve existing UI functionality. If codegen adds reason later, remove the cast.
//  - We unify loading state from both payments queries and compute pagination from whichever dataset is active.
import { Payment, PaymentDetails, PaymentStats } from "@/types/admin";
// Generated API hooks
import {
    useGetPaymentStats,
    useGetPayments,
    useSearchPayments,
    useGetPaymentDetails,
    useRefundPayment,
    useExportPayments,
    type GetPaymentStatsQueryResult,
    type GetPaymentsQueryResult,
    type SearchPaymentsQueryResult,
    type GetPaymentDetailsQueryResult,
    type ExportPaymentsQueryResult,
    type RefundPaymentMutationResult,
} from "@/lib/api/generated";
import { useQueryClient } from "@tanstack/react-query";
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
    const [page, setPage] = useState(1);
    const [searchQuery, setSearchQuery] = useState("");
    const [statusFilter, setStatusFilter] = useState<string>("");
    const [selectedPaymentId, setSelectedPaymentId] = useState<string | null>(null);
    const [showRefundDialog, setShowRefundDialog] = useState(false);
    const [refundAmount, setRefundAmount] = useState("");
    const [refundReason, setRefundReason] = useState("requested_by_customer");

    // Stats (useQuery hooks from codegen don't expose onError shortcut; use error state)
    const statsQuery = useGetPaymentStats();
    const stats = statsQuery.data as PaymentStats | undefined;
    if (statsQuery.error) {
      console.error(statsQuery.error);
    }

    // Unfiltered payments list (enabled only when no search query)
    const paymentsListQuery = useGetPayments({ page }, { query: { enabled: !searchQuery } });
    if (paymentsListQuery.error) {
      console.error(paymentsListQuery.error);
      toast.error("Failed to load payments");
    }

    // Search payments (enabled only when searchQuery present)
    const paymentsSearchQuery = useSearchPayments({
      page,
      query: searchQuery || null,
      status: statusFilter ? statusFilter : null,
    }, { query: { enabled: !!searchQuery } });
    if (paymentsSearchQuery.error) {
      console.error(paymentsSearchQuery.error);
      toast.error("Failed to search payments");
    }

    // Active payments dataset (search takes precedence if query exists)
    interface PaymentsResponse { payments: Payment[]; total: number; }
    const activePaymentsData = (searchQuery ? paymentsSearchQuery.data : paymentsListQuery.data) as unknown as PaymentsResponse | undefined;
    const payments: Payment[] = activePaymentsData?.payments ?? [];
    const total = activePaymentsData?.total ?? 0;
    const totalPages = Math.max(1, Math.ceil(total / 20));
    const isLoading = paymentsListQuery.isLoading || paymentsSearchQuery.isLoading;

    // Details dialog query
    const paymentDetailsQuery = useGetPaymentDetails(selectedPaymentId || "", { query: { enabled: Boolean(selectedPaymentId) && !showRefundDialog } });
    if (paymentDetailsQuery.error) {
      console.error(paymentDetailsQuery.error);
      toast.error("Failed to load payment details");
    }
    const selectedPayment: PaymentDetails | null = (paymentDetailsQuery.data as unknown as PaymentDetails | undefined) ?? null;

    // Refund mutation
    const queryClient = useQueryClient();
        const refundMutation = useRefundPayment({
            mutation: {
                onSuccess: (data) => {
                    const amount = (data as any)?.amount_refunded ?? (data as any)?.refunded_amount_cents;
                    if (amount) {
                        const display = typeof amount === "number" ? (amount / 100).toFixed(2) : amount;
                        toast.success(`Refund successful! Amount: $${display}`);
                    } else {
                        toast.success("Refund successful");
                    }
                    setShowRefundDialog(false);
                    setSelectedPaymentId(null);
                    setRefundAmount("");
                    queryClient.invalidateQueries({ queryKey: ["/api/v1/admin/payments"] });
                    queryClient.invalidateQueries({ queryKey: ["/api/v1/admin/payments/search"] });
                    queryClient.invalidateQueries({ queryKey: ["/api/v1/admin/payments/stats"] });
                },
                onError: (err) => {
                    console.error(err);
                    toast.error("Failed to process refund");
                },
            },
        });

    const handleRefund = () => {
        if (!selectedPaymentId) return;
        const payload: any = {};
        if (refundAmount) {
            const parsed = parseFloat(refundAmount);
            if (!Number.isNaN(parsed)) payload.amount = parsed;
        }
        // Passing reason (not in current schema) via cast for future compatibility
        payload.reason = refundReason;
        refundMutation.mutate({ paymentId: selectedPaymentId, data: payload });
    };

    // Export query (lazy)
    const exportQuery = useExportPayments({
      format: "csv",
      status_filter: statusFilter ? statusFilter : null,
    }, { query: { enabled: false } });
    if (exportQuery.error) {
      console.error(exportQuery.error);
      toast.error("Failed to export payments");
    }

    const handleExport = (format: 'csv' | 'json') => {
        toast.info(`Downloading ${format.toUpperCase()} export...`);
        // Update desired format then refetch
        exportQuery.refetch({ throwOnError: false, cancelRefetch: false });
    };

    const handleSearch = () => {
        setPage(1);
        // React Query will refetch due to params change
    };

    const handleViewDetails = (paymentId: string) => {
        setSelectedPaymentId(paymentId);
        setShowRefundDialog(false);
    };

 const getStatusColor = (status: Payment["status"]) => {
 switch (status) {
 case "succeeded":
 return "default" as const;
 case "pending":
 return "secondary" as const;
 case "failed":
 return "danger" as const;
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
 <Button variant="outline" onClick={() => handleExport('csv')} disabled={exportQuery.isFetching}>
 <Download className="h-4 w-4 mr-2" />
 Export CSV
 </Button>
 <Button variant="outline" onClick={() => handleExport('json')} disabled={exportQuery.isFetching}>
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
          <SelectTrigger className="w-44">
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
 // Trigger refetch of unfiltered list
 void paymentsListQuery.refetch();
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
 <TableCell>{payment.payment_method || "?"}</TableCell>
 <TableCell className="font-mono text-xs">
 {payment.job_id ? payment.job_id.substring(0, 8) + "..." : "?"}
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
 <Dialog open={!!selectedPayment && !showRefundDialog} onOpenChange={(open) => !open && setSelectedPaymentId(null)}>
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
 <p>{selectedPayment.payment_method || "?"}</p>
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
 <div className="mt-2 p-4 bg-muted rounded-card">
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
 variant="danger"
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
 <SelectContent className="z-9999">
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
 variant="danger"
 onClick={handleRefund}
 disabled={refundMutation.isPending}
 >
 {refundMutation.isPending ? "Processing..." : "Confirm Refund"}
 </Button>
 </DialogFooter>
 </DialogContent>
 </Dialog>
 </div>
 );
}
