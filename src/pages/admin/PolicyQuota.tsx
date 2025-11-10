import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  AgentAclMetric,
  BlockedCallMetric,
  PolicyQuotaMetrics,
  QuotaUsageMetric,
} from "@/types/admin";
import { useMemo } from "react";
import { useGetPolicyQuotaMetrics } from "@/lib/api/generated";

const formatPercent = (used: number, limit: number) => {
  if (!limit) {
    return 0;
  }
  return Math.min(100, Math.round((used / limit) * 100));
};

const formatTimestamp = (value?: string) => {
  if (!value) {
    return "—";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "—";
  }
  return date.toLocaleString();
};

const summarizePayload = (payload?: string) => {
  if (!payload) {
    return "";
  }
  return payload.length > 140 ? `${payload.slice(0, 137)}…` : payload;
};

const PolicyQuotaDashboard = () => {
  const { data, isLoading, error } = useGetPolicyQuotaMetrics();

  const metrics: PolicyQuotaMetrics | null = data ?? null;
  const quotas: QuotaUsageMetric[] = metrics?.quotas ?? [];
  const blocked: BlockedCallMetric[] = metrics?.blocked_calls ?? [];
  const agentAcls: AgentAclMetric[] = metrics?.agent_acls ?? [];

  const summaryCards = useMemo(
    () => [
      {
        label: "Active policies",
        value: metrics?.summary.total_policies ?? 0,
        tone: "text-primary",
      },
      {
        label: "Blocked calls (24h)",
        value: metrics?.summary.total_blocked ?? 0,
        tone: "text-danger",
      },
      {
        label: "Active overrides",
        value: metrics?.summary.active_overrides ?? 0,
        tone: "text-accent",
      },
    ],
    [
      metrics?.summary.active_overrides,
      metrics?.summary.total_blocked,
      metrics?.summary.total_policies,
    ],
  );

  return (
    <div className="p-8 space-y-6">
      <div>
        <h1 className="text-3xl font-bold gradient-text-primary">
          Policy & Quota Analytics
        </h1>
        <p className="text-muted-foreground mt-2 max-w-2xl">
          Monitor live quota burn, investigate blocked calls, and audit agent
          access lists sourced from the policy engine.
        </p>
      </div>

      {isLoading && (
        <Card className="bg-card">
          <CardContent className="py-10 text-center text-muted-foreground">
            Loading policy telemetry…
          </CardContent>
        </Card>
      )}

      {error && !isLoading && (
        <Card className="bg-card border-accent/30">
          <CardContent className="py-10 text-center">
            <p className="text-muted-foreground text-lg mb-2">
              Failed to Load Policy & Quota Metrics
            </p>
            <p className="text-xs text-danger mt-4">
              {error instanceof Error ? error.message : "Unknown error"}
            </p>
          </CardContent>
        </Card>
      )}

      {!isLoading && !error && metrics && (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            {summaryCards.map((card) => (
              <Card key={card.label} className="bg-card border-border/60">
                <CardContent className="py-6">
                  <p className="text-sm text-muted-foreground">{card.label}</p>
                  <p className={`text-3xl font-semibold ${card.tone}`}>
                    {card.value}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="bg-card">
            <CardHeader>
              <CardTitle>Quota Utilization</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {quotas.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No quota data is available yet.
                </p>
              ) : (
                quotas.map((quota) => {
                  const percent = formatPercent(quota.used, quota.limit);
                  return (
                    <div key={quota.policy_id} className="space-y-2">
                      <div className="flex flex-col justify-between gap-2 md:flex-row md:items-center">
                        <div>
                          <p className="font-medium text-foreground">
                            {quota.policy_name}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            Window: {quota.window} • Limit:{" "}
                            {quota.limit.toLocaleString()}
                          </p>
                        </div>
                        <Badge
                          className={
                            percent >= 90
                              ? "bg-danger text-danger-foreground"
                              : "bg-secondary text-secondary-foreground"
                          }
                        >
                          {percent}% used
                        </Badge>
                      </div>
                      <Progress value={percent} />
                      <p className="text-xs text-muted-foreground">
                        Consumed {quota.used.toLocaleString()} of{" "}
                        {quota.limit.toLocaleString()} • Reset{" "}
                        {formatTimestamp(quota.reset_at)}
                      </p>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>

          <Card className="bg-card">
            <CardHeader>
              <CardTitle>Recent Blocked Calls</CardTitle>
            </CardHeader>
            <CardContent>
              {blocked.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No calls have been blocked in the current window.
                </p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-40">When</TableHead>
                      <TableHead>Agent</TableHead>
                      <TableHead>Tool</TableHead>
                      <TableHead>Policy</TableHead>
                      <TableHead>Reason</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {blocked.slice(0, 10).map((entry) => (
                      <TableRow key={entry.id} className="border-border/60">
                        <TableCell className="text-sm text-muted-foreground">
                          {formatTimestamp(entry.occurred_at)}
                        </TableCell>
                        <TableCell className="font-medium text-foreground">
                          {entry.agent_name}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {entry.tool_name ?? "—"}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {entry.policy_name ?? "—"}
                        </TableCell>
                        <TableCell className="text-sm text-muted-foreground">
                          {summarizePayload(entry.reason)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>

          <Card className="bg-card">
            <CardHeader>
              <CardTitle>Agent Access Controls</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 md:grid-cols-2">
              {agentAcls.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No agent access lists are defined.
                </p>
              ) : (
                agentAcls.map((acl) => (
                  <Card
                    key={acl.agent_id}
                    className="border border-border/60 bg-background"
                  >
                    <CardHeader>
                      <CardTitle className="text-lg">
                        {acl.agent_name}
                      </CardTitle>
                      <p className="text-xs text-muted-foreground">
                        Last updated {formatTimestamp(acl.last_updated)}
                      </p>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                          Allowed tools
                        </p>
                        {acl.allowed_tools.length === 0 ? (
                          <p className="text-sm text-muted-foreground mt-1">
                            No tools permitted.
                          </p>
                        ) : (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {acl.allowed_tools.map((tool) => (
                              <Badge
                                key={tool}
                                variant="outline"
                                className="border-muted text-muted-foreground"
                              >
                                {tool}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                          Blocked tools
                        </p>
                        {acl.blocked_tools.length === 0 ? (
                          <p className="text-sm text-muted-foreground mt-1">
                            No explicit blocks.
                          </p>
                        ) : (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {acl.blocked_tools.map((tool) => (
                              <Badge
                                key={tool}
                                variant="danger"
                                className="bg-danger/10 text-danger border-danger/20"
                              >
                                {tool}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                      {acl.notes && (
                        <p className="text-xs text-muted-foreground">
                          {acl.notes}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                ))
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
};

export default PolicyQuotaDashboard;
