import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { MessageSquare, AlertCircle, Clock, Send, ExternalLink, Zap } from "lucide-react";
import { CannedReply, SupportTicket, TicketMessage } from "@/types/admin";

export default function Support() {
  const [filters, setFilters] = useState<{
    status?: string;
    priority?: string;
    category?: string;
  }>({});
  const [selectedTicket, setSelectedTicket] = useState<string | null>(null);
  const [replyContent, setReplyContent] = useState("");
  const [showCannedReplies, setShowCannedReplies] = useState(false);
  const queryClient = useQueryClient();

  const {
    data: ticketsData,
    isLoading: isTicketsLoading,
  } = useQuery({
    queryKey: ["support-tickets", filters],
    queryFn: () => apiClient.getTickets(1, filters),
  });

  const { data: ticketDetail } = useQuery({
    queryKey: ["support-ticket", selectedTicket],
    queryFn: () => apiClient.getTicket(selectedTicket!),
    enabled: Boolean(selectedTicket),
  });

  const { data: cannedRepliesData } = useQuery({
    queryKey: ["canned-replies"],
    queryFn: () => apiClient.getCannedReplies(),
  });

  const replyMutation = useMutation({
    mutationFn: ({ ticketId, content }: { ticketId: string; content: string }) =>
      apiClient.replyToTicket(ticketId, content),
    onSuccess: () => {
      toast.success("Reply sent successfully");
      setReplyContent("");
      queryClient.invalidateQueries({ queryKey: ["support-ticket"] });
    },
    onError: () => toast.error("Failed to send reply"),
  });

  const statusMutation = useMutation({
    mutationFn: ({ ticketId, status }: { ticketId: string; status: string }) =>
      apiClient.updateTicketStatus(ticketId, status),
    onSuccess: () => {
      toast.success("Status updated");
      queryClient.invalidateQueries({ queryKey: ["support-tickets"] });
      queryClient.invalidateQueries({ queryKey: ["support-ticket"] });
    },
    onError: () => toast.error("Failed to update status"),
  });

  const handleReply = () => {
    if (selectedTicket && replyContent.trim()) {
      replyMutation.mutate({ ticketId: selectedTicket, content: replyContent });
    }
  };

  const handleStatusChange = (status: string) => {
    if (selectedTicket) {
      statusMutation.mutate({ ticketId: selectedTicket, status });
    }
  };

  const applyCannedReply = (content: string) => {
    setReplyContent(content);
    setShowCannedReplies(false);
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case "urgent":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case "high":
        return <AlertCircle className="h-4 w-4 text-orange-500" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      open: "bg-blue-500/10 text-blue-500 border-blue-500/20",
      in_progress: "bg-purple-500/10 text-purple-500 border-purple-500/20",
      waiting: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
      resolved: "bg-green-500/10 text-green-500 border-green-500/20",
      closed: "bg-gray-500/10 text-muted-foreground",
    };
    return colors[status] || colors.open;
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      urgent: "bg-red-500/10 text-red-500 border-red-500/20",
      high: "bg-orange-500/10 text-orange-500 border-orange-500/20",
      medium: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
      low: "bg-gray-500/10 text-muted-foreground",
    };
    return colors[priority] || colors.medium;
  };

  const handleFilterChange = (key: "status" | "priority" | "category", value: string) => {
    setFilters((current) => ({
      ...current,
      [key]: value === "all" ? undefined : value,
    }));
  };

  const tickets = ticketsData?.tickets ?? [];

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
          Support Tools
        </h1>
        <p className="text-muted-foreground mt-2">Manage customer tickets and provide support</p>
      </div>

      <Card className="bg-card">
        <CardHeader>
          <CardTitle>Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-3">
            <Select
              value={filters.status ?? "all"}
              onValueChange={(value) => handleFilterChange("status", value)}
            >
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="waiting">Waiting</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
                <SelectItem value="closed">Closed</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={filters.priority ?? "all"}
              onValueChange={(value) => handleFilterChange("priority", value)}
            >
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={filters.category ?? "all"}
              onValueChange={(value) => handleFilterChange("category", value)}
            >
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="technical">Technical</SelectItem>
                <SelectItem value="billing">Billing</SelectItem>
                <SelectItem value="content">Content</SelectItem>
                <SelectItem value="account">Account</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4">
        {isTicketsLoading ? (
          <Card className="bg-card">
            <CardContent className="p-6 text-center text-muted-foreground">
              Loading tickets...
            </CardContent>
          </Card>
        ) : tickets.length === 0 ? (
          <Card className="bg-card">
            <CardContent className="p-6 text-center text-muted-foreground">
              No tickets found for the selected filters
            </CardContent>
          </Card>
        ) : (
          tickets.map((ticket: SupportTicket) => (
            <Card
              key={ticket.id}
              className="bg-card hover:shadow-glow transition-shadow cursor-pointer"
              onClick={() => setSelectedTicket(ticket.id)}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-3">
                      {getPriorityIcon(ticket.priority)}
                      <h3 className="font-semibold">{ticket.subject}</h3>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {ticket.user_email} • {new Date(ticket.created_at).toLocaleString()}
                    </p>
                    <div className="flex gap-2">
                      <Badge className={getStatusColor(ticket.status)}>
                        {ticket.status.replace("_", " ")}
                      </Badge>
                      <Badge className={getPriorityColor(ticket.priority)}>{ticket.priority}</Badge>
                      <Badge variant="outline">{ticket.category}</Badge>
                    </div>
                    {ticket.context && (
                      <div className="flex gap-2 mt-2">
                        {ticket.context.job_id && (
                          <Badge variant="secondary" className="text-xs">
                            Job: {ticket.context.job_id.slice(0, 8)}
                          </Badge>
                        )}
                        {ticket.context.content_id && (
                          <Badge variant="secondary" className="text-xs">
                            Content: {ticket.context.content_id.slice(0, 8)}
                          </Badge>
                        )}
                        {ticket.context.payment_id && (
                          <Badge variant="secondary" className="text-xs">
                            Payment: {ticket.context.payment_id.slice(0, 8)}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                  <MessageSquare className="h-5 w-5 text-muted-foreground" />
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      <Dialog open={!!selectedTicket} onOpenChange={() => setSelectedTicket(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{ticketDetail?.subject}</DialogTitle>
            <DialogDescription>
              Ticket #{selectedTicket?.slice(0, 8)} • {ticketDetail?.user_email}
            </DialogDescription>
          </DialogHeader>

          {ticketDetail && (
            <div className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-muted-foreground">Submitted</p>
                    <p className="text-sm">{new Date(ticketDetail.created_at).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Last Updated</p>
                    <p className="text-sm">{new Date(ticketDetail.updated_at).toLocaleString()}</p>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground">Status</label>
                    <Select
                      value={ticketDetail.status}
                      onValueChange={(value) => handleStatusChange(value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="open">Open</SelectItem>
                        <SelectItem value="in_progress">In Progress</SelectItem>
                        <SelectItem value="waiting">Waiting</SelectItem>
                        <SelectItem value="resolved">Resolved</SelectItem>
                        <SelectItem value="closed">Closed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-3">
                  <div>
                    <p className="text-xs text-muted-foreground">Priority</p>
                    <Badge className={getPriorityColor(ticketDetail.priority)}>
                      {ticketDetail.priority}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Category</p>
                    <Badge variant="outline">{ticketDetail.category}</Badge>
                  </div>
                </div>
              </div>

              {ticketDetail.context && (
                <Card className="bg-card">
                  <CardHeader>
                    <CardTitle className="text-sm">Context</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {ticketDetail.context.job_id && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Job ID</span>
                        <Button size="sm" variant="ghost" asChild>
                          <a href={`/admin/agents?job=${ticketDetail.context.job_id}`}>
                            {ticketDetail.context.job_id.slice(0, 8)}
                            <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                        </Button>
                      </div>
                    )}
                    {ticketDetail.context.content_id && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Content ID</span>
                        <Button size="sm" variant="ghost" asChild>
                          <a href={`/admin/content?id=${ticketDetail.context.content_id}`}>
                            {ticketDetail.context.content_id.slice(0, 8)}
                            <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                        </Button>
                      </div>
                    )}
                    {ticketDetail.context.payment_id && (
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Payment ID</span>
                        <Button size="sm" variant="ghost" asChild>
                          <a href={`/admin/payments?id=${ticketDetail.context.payment_id}`}>
                            {ticketDetail.context.payment_id.slice(0, 8)}
                            <ExternalLink className="h-3 w-3 ml-1" />
                          </a>
                        </Button>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              <Separator />

              <div className="space-y-4">
                <h4 className="font-semibold">Conversation</h4>
                {ticketDetail.messages?.map((message: TicketMessage) => (
                  <div
                    key={message.id}
                    className={`p-4 rounded-lg ${
                      message.author_type === "admin"
                        ? "bg-primary/5 border-l-2 border-primary"
                        : "bg-muted"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">
                        {message.author_name}
                        {message.author_type === "admin" && (
                          <Badge variant="outline" className="ml-2 text-xs">
                            Admin
                          </Badge>
                        )}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {new Date(message.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                ))}
              </div>

              <Separator />

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">Reply</h4>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setShowCannedReplies(!showCannedReplies)}
                  >
                    <Zap className="h-3 w-3 mr-1" />
                    Canned Replies
                  </Button>
                </div>

                {showCannedReplies && (
                  <div className="grid gap-2 p-3 bg-muted rounded-lg">
                    {cannedRepliesData?.replies?.map((reply: CannedReply) => (
                      <Button
                        key={reply.id}
                        size="sm"
                        variant="ghost"
                        className="justify-start h-auto p-2 text-left"
                        onClick={() => applyCannedReply(reply.content)}
                      >
                        <div>
                          <div className="font-medium text-xs">{reply.title}</div>
                          <div className="text-xs text-muted-foreground line-clamp-1">
                            {reply.content}
                          </div>
                        </div>
                      </Button>
                    ))}
                  </div>
                )}

                <Textarea
                  placeholder="Type your reply..."
                  value={replyContent}
                  onChange={(e) => setReplyContent(e.target.value)}
                  rows={4}
                />
                <Button
                  onClick={handleReply}
                  disabled={!replyContent.trim() || replyMutation.isPending}
                  className="w-full"
                >
                  <Send className="h-4 w-4 mr-2" />
                  Send Reply
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
