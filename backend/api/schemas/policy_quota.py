"""Pydantic schemas for Policy & Quota Analytics."""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class QuotaUsageMetric(BaseModel):
    """Quota usage metrics for a specific policy."""

    policy_id: str
    policy_name: str
    window: str
    limit: int
    used: int
    reset_at: Optional[str] = None


class BlockedCallMetric(BaseModel):
    """Metrics for blocked API calls."""

    id: str
    occurred_at: str
    agent_name: str
    tool_name: Optional[str] = None
    policy_name: Optional[str] = None
    reason: str
    payload_summary: Optional[str] = None


class AgentAclMetric(BaseModel):
    """Agent Access Control List metrics."""

    agent_id: str
    agent_name: str
    allowed_tools: List[str]
    blocked_tools: List[str]
    last_updated: str
    notes: Optional[str] = None


class PolicyQuotaSummary(BaseModel):
    """Summary statistics for policy and quota metrics."""

    total_policies: int
    total_blocked: int
    active_overrides: int


class PolicyQuotaMetrics(BaseModel):
    """Complete policy and quota analytics response."""

    summary: PolicyQuotaSummary
    quotas: List[QuotaUsageMetric]
    blocked_calls: List[BlockedCallMetric]
    agent_acls: List[AgentAclMetric]
