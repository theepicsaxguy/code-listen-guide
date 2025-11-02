"""Episode model representing a podcast episode derived from a codebase.

This is part of the transition from file-based chapters (linear) to
relationship/architecture-based episodes (graph/narrative driven).

MVP decisions:
 - Store clusters, dependency graph, hooks, objectives as JSONB for agility
 - Avoid relationships until other parts of system consume them
 - Keep status simple; future states (review, regenerating) can be added later
"""

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    ForeignKey,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum

from backend.db.base import Base


class EpisodeStatus(str, enum.Enum):
    PENDING = "pending"
    PLANNING = "planning"
    SCRIPTING = "scripting"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"


class Episode(Base):
    """Represents a planned / generated podcast episode.

    Episodes are thematic; they group related files and concepts instead of
    mirroring directory layout. Dialogue scripts (two‑host) are generated
    per episode.
    """

    __tablename__ = "episodes"

    # Identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), index=True, nullable=False)
    episode_number = Column(Integer, nullable=False)  # 1-based ordering within job
    title = Column(String(255), nullable=False)
    narrative_theme = Column(Text, nullable=False)  # Human readable theme/story focus

    # Structure / analysis artifacts
    file_clusters = Column(JSONB)  # {cluster_name: [files...]}
    dependency_graph = Column(JSONB)  # {file: [dependencies...]}
    architectural_boundary = Column(String(255))  # e.g. "Authentication Layer"

    # Planning / educational metadata
    conversation_hooks = Column(JSONB)  # [questions / prompts driving dialogue]
    learning_objectives = Column(JSONB)  # [learning goals]
    goals = Column(JSONB)  # High-level outcome goals for the episode (future use / editable)

    # Dependency planning (graph-level semantics for Episode relationships)
    dependency_inputs = Column(JSONB)  # Concepts / components this episode depends ON (ingress)
    dependency_outputs = Column(JSONB)  # Concepts / components this episode produces / clarifies (egress)
    depends_on = Column(JSONB)  # Episode IDs (UUID strings) that must precede this one (planning time)
    leads_to = Column(JSONB)  # Episode IDs that commonly follow from this one (narrative suggestions)

    # Scheduling / pacing
    estimated_duration_minutes = Column(Integer)  # Planner's duration estimate for balancing arc

    # Generation metrics
    estimated_tokens = Column(Integer)  # Est tokens for dialogue gen
    status = Column(Enum(EpisodeStatus), default=EpisodeStatus.PENDING, index=True)

    # Outputs
    dialogue_script = Column(Text)  # Two-host conversation script (raw)
    audio_url = Column(String(500))
    duration_seconds = Column(Integer)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):  # pragma: no cover - representational
        return f"<Episode {self.id} job={self.job_id} #{self.episode_number} {self.title}>"
