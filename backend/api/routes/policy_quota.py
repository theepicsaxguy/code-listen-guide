"""Admin API for Policy & Quota Analytics."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.dependencies import require_admin
from backend.api.schemas.policy_quota import (
    AgentAclMetric,
    BlockedCallMetric,
    PolicyQuotaMetrics,
    PolicyQuotaSummary,
    QuotaUsageMetric,
)
from backend.db.session import get_db
from backend.models.agent_registry import AgentRegistry


router = APIRouter(prefix="/api/v1/admin/policy-quota", tags=["admin", "policy"])


@router.get("/metrics", operation_id="getPolicyQuotaMetrics", response_model=PolicyQuotaMetrics)
async def get_policy_quota_metrics(
    db: Session = Depends(get_db),
    _current_admin=Depends(require_admin),
):
    """
    Get comprehensive policy and quota analytics.

    Returns metrics about:
    - Policy usage and quota consumption
    - Blocked calls due to policy violations
    - Agent access control lists (ACLs)

    NOTE: This is a simplified implementation that returns example/mock data.
    In a production system, this would query actual policy enforcement logs,
    quota tracking tables, and ACL configurations.
    """

    # TODO: Replace with actual data from policy enforcement system
    # For now, return example data to demonstrate the dashboard

    # Get agents from the database for realistic agent names
    agents = db.query(AgentRegistry).limit(5).all()
    agent_acls: List[AgentAclMetric] = []

    for agent in agents:
        # Use actual agent data where available
        allowed_tools = []
        if hasattr(agent, 'allowed_tools') and agent.allowed_tools:
            allowed_tools = agent.allowed_tools if isinstance(agent.allowed_tools, list) else []

        agent_acls.append(
            AgentAclMetric(
                agent_id=str(agent.id),
                agent_name=agent.name,
                allowed_tools=allowed_tools or ["Read", "Write", "Execute", "Delete"],
                blocked_tools=[] if allowed_tools else ["SystemCall", "NetworkAccess"],
                last_updated=datetime.utcnow().isoformat(),
                notes=f"ACL for {agent.name}" if allowed_tools else None,
            )
        )

    # Generate example quota metrics
    quotas: List[QuotaUsageMetric] = [
        QuotaUsageMetric(
            policy_id="policy-api-rate-limit",
            policy_name="API Rate Limit",
            window="1 hour",
            limit=10000,
            used=7542,
            reset_at=(datetime.utcnow() + timedelta(minutes=23)).isoformat(),
        ),
        QuotaUsageMetric(
            policy_id="policy-storage-quota",
            policy_name="Storage Quota",
            window="monthly",
            limit=100000000000,  # 100GB in bytes
            used=45678900000,    # ~45GB
            reset_at=(datetime.utcnow() + timedelta(days=12)).isoformat(),
        ),
        QuotaUsageMetric(
            policy_id="policy-job-limit",
            policy_name="Concurrent Jobs",
            window="realtime",
            limit=50,
            used=23,
            reset_at=None,  # Realtime quotas don't reset
        ),
    ]

    # Generate example blocked call metrics
    blocked_calls: List[BlockedCallMetric] = [
        BlockedCallMetric(
            id="blocked-001",
            occurred_at=(datetime.utcnow() - timedelta(hours=2)).isoformat(),
            agent_name=agents[0].name if agents else "ExampleAgent",
            tool_name="FileSystem.Write",
            policy_name="Write Protection Policy",
            reason="Attempted write to protected directory",
            payload_summary="/etc/system.conf",
        ),
        BlockedCallMetric(
            id="blocked-002",
            occurred_at=(datetime.utcnow() - timedelta(hours=5)).isoformat(),
            agent_name=agents[1].name if len(agents) > 1 else "AnotherAgent",
            tool_name="Network.Connect",
            policy_name="Network Access Policy",
            reason="External network access not permitted for this agent",
            payload_summary="https://external-api.example.com",
        ),
    ]

    # Summary statistics
    summary = PolicyQuotaSummary(
        total_policies=len(quotas) + 5,  # Include additional policies not shown
        total_blocked=len(blocked_calls),
        active_overrides=0,  # No overrides in this example
    )

    return PolicyQuotaMetrics(
        summary=summary,
        quotas=quotas,
        blocked_calls=blocked_calls,
        agent_acls=agent_acls,
    )
