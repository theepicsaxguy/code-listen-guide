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
import { apiClient } from "@/lib/api";
import { Payment } from "@/types/admin";
import { toast } from "sonner";

export default function AdminPayments() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);

  useEffect(() => {
    const fetchPayments = async () => {
      setIsLoading(true);
      try {
        const data = await apiClient.getPayments(page);
        setPayments(data.payments || []);
      } catch (error) {
        toast.error("Failed to load payments");
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    };

    void fetchPayments();
  }, [page]);

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

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Payment Management</h1>
        <p className="text-muted-foreground mt-1">View and manage all payment transactions</p>
      </div>

      <div className="bg-card border border-border rounded-lg shadow-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Transaction ID</TableHead>
              <TableHead>User ID</TableHead>
              <TableHead>Amount</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Description</TableHead>
              <TableHead>Date</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8">
                  Loading payments...
                </TableCell>
              </TableRow>
            ) : payments.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                  No payments found
                </TableCell>
              </TableRow>
            ) : (
              payments.map((payment) => (
                <TableRow key={payment.id}>
                  <TableCell className="font-mono text-sm">{payment.id}</TableCell>
                  <TableCell className="font-mono text-sm">{payment.user_id}</TableCell>
                  <TableCell className="font-semibold">
                    {payment.currency.toUpperCase()} {payment.amount.toFixed(2)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={getStatusColor(payment.status)}>{payment.status}</Badge>
                  </TableCell>
                  <TableCell>{payment.description || "—"}</TableCell>
                  <TableCell>{new Date(payment.created_at).toLocaleString()}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          onClick={() => setPage((value) => Math.max(1, value - 1))}
          disabled={page === 1}
        >
          Previous
        </Button>
        <span className="text-sm text-muted-foreground">Page {page}</span>
        <Button variant="outline" onClick={() => setPage((value) => value + 1)}>
          Next
        </Button>
      </div>
    </div>
  );
}
