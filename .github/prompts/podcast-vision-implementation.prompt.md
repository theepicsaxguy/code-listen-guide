---
name: "Git Repository to Podcast - Full Vision Implementation Plan"
description: "Complete roadmap to transform the current audiobook system into a podcast generation platform with conversational dialogue, relationship-based episodes, and hard approval gates"
---

# Git Repository to Podcast — Full Vision Implementation Plan

## Executive Summary

**Current State:** Traditional audiobook pipeline (file-based chapters, single-narrator scripts, one approval gate)

**Goal State:** Podcast generation platform (relationship-based episodes, two-host dialogue, three approval gates)

**Alignment:** ~20% infrastructure overlap, 0% overlap in user experience and output format

**Total Effort:** 49 development days (~10 calendar weeks with 1 developer)

---

## Critical Gap Analysis

### 🔴 Tier 1: Blocking Vision Implementation

1. **No Pre-Agent Preview Flow** (0% implemented)
   - Missing: README + file tree shown BEFORE job creation
   - Impact: Users commit without seeing what they're getting
   - Effort: 2-3 days

2. **No Scope Selection UI** (10% implemented)
   - Missing: File/folder picker, language priority selector
   - Impact: Users can't control what gets processed
   - Effort: 3-4 days

3. **No Real Token Estimation** (20% implemented - endpoint exists)
   - Missing: Actual token counting, cost calculation
   - Impact: Runaway costs, no user trust
   - Effort: 2-3 days

4. **Chapter Model Instead of Episode Model** (0% implemented)
   - Missing: Relationship-based planning, dependency analysis
   - Impact: Output is file-by-file, not thematic narratives
   - Effort: 5-7 days

5. **Narration Instead of Podcast Dialogue** (0% implemented)
   - Missing: Two-host conversation format, persona system
   - Impact: Output is audiobook, not podcast
   - Effort: 7-10 days

### 🟡 Tier 2: Important But Not Blocking

6. **No Queue System** (0% implemented)
   - Missing: Job queuing, resource allocation
   - Effort: 3-4 days

7. **No Multi-Language Stack Handling** (0% implemented)
   - Missing: Primary language selection for mixed codebases
   - Effort: 2 days

8. **Plugin Manifests Missing** (60% implemented - core exists)
   - Missing: Declarative plugin.yaml, semantic versioning
   - Effort: 3-4 days

---

## Architecture Comparison

| Aspect | Current State | Goal Vision | Alignment |
|--------|--------------|-------------|-----------|
| **Pre-Processing** | Direct job creation | README + file tree preview | ❌ 0% |
| **Scope Control** | Depth tier only | User selects files/modules | ❌ 10% |
| **Cost Gates** | No upfront estimate | Token count before queue | ❌ 20% (endpoint exists) |
| **Unit of Work** | Chapter (file-based) | Episode (relationship-based) | ❌ 0% |
| **Output Format** | Narration script | Two-host podcast dialogue | ❌ 0% |
| **Tool Model** | Database + source | Plugin manifests in code | ⚠️ 60% |
| **Approval Gates** | Outline approval only | 3 gates (scope, cost, final) | ⚠️ 33% |
| **Agent Specialization** | 6 workflow agents | Many small agents | ⚠️ 70% |

---

## Sprint 1: Trust & Control Foundation (2 weeks)

**Goal:** Users see what they're getting before committing any tokens

### Week 1: Pre-Agent Preview Flow

**Day 1-2: Wire Parse Endpoint to Submit Flow**

Files to modify:
- `src/pages/Submit.tsx` — Add preview step before job creation
- `src/lib/api.ts` — Add `parseRepository()` method

```typescript
// src/lib/api.ts
async parseRepository(repoUrl: string, gitRef: string = 'main'): Promise<ParseResult> {
  return this.request('/parse/repository', {
    method: 'POST',
    body: { repo_url: repoUrl, git_ref: gitRef }
  });
}
```

Create new components:
- `src/pages/RepositoryPreview.tsx` — Display README and file tree
- `src/components/RepositoryBrowser.tsx` — Already exists, wire it up
- `src/components/ReadmeViewer.tsx` — Markdown rendering with syntax highlighting

User Flow:
1. User enters GitHub URL in Submit.tsx
2. Click "Preview Repository" button
3. Navigate to RepositoryPreview.tsx
4. Shows README content + file tree (from parse endpoint)
5. User clicks "Continue to Scope Selection"

**Day 3-5: Build Scope Selection Interface**

Files to create:
- `src/pages/ScopeSelection.tsx` — File picker with language priority
- `src/components/FileTreeSelector.tsx` — Interactive tree with checkboxes
- `src/components/LanguagePrioritySelector.tsx` — Dropdown for mixed stacks

Database schema changes:
```python
# backend/models/job.py
class Job(Base):
    # ... existing fields ...
    
    # NEW: Scope selection
    selected_files = Column(JSONB, nullable=True)  # User-selected file paths
    excluded_patterns = Column(JSONB, nullable=True)  # User exclusions (e.g., ["*.test.ts"])
    primary_language = Column(String, nullable=True)  # For mixed stacks
```

Migration:
```bash
# Create Alembic migration
cd backend
alembic revision -m "add_scope_selection_fields"
# Edit migration file to add columns
alembic upgrade head
```

API schema updates:
```python
# backend/api/schemas/job.py
class JobCreate(BaseModel):
    repo_url: HttpUrl
    depth_tier: str
    git_ref: str = "main"
    
    # NEW fields
    selected_files: Optional[List[str]] = None
    excluded_patterns: Optional[List[str]] = None
    primary_language: Optional[str] = None
```

### Week 2: Token Estimation & Cost Gate

**Day 6-8: Implement Real Token Estimation**

Files to modify:
- `backend/tools/db_tools.py` — Replace `estimate_job_cost()` placeholder
- `backend/services/token_estimator.py` — NEW service for token counting

```python
# backend/services/token_estimator.py
import tiktoken
from typing import List, Dict

class TokenEstimator:
    def __init__(self, model: str = "gpt-4"):
        self.encoder = tiktoken.encoding_for_model(model)
    
    def estimate_llm_tokens(self, file_contents: List[str]) -> int:
        """Estimate tokens for code analysis and script generation."""
        total_tokens = 0
        for content in file_contents:
            total_tokens += len(self.encoder.encode(content))
        
        # Add overhead for prompts (outline, script generation, etc.)
        overhead_multiplier = 1.5  # 50% overhead for system prompts
        return int(total_tokens * overhead_multiplier)
    
    def estimate_tts_tokens(self, script_word_count: int) -> int:
        """Estimate TTS characters needed."""
        # Average: 150 words per minute, 20 minutes per chapter
        chars_per_chapter = script_word_count * 5  # ~5 chars per word
        return chars_per_chapter
    
    def calculate_cost(self, llm_tokens: int, tts_chars: int) -> Dict:
        """Calculate costs based on OpenAI/Anthropic pricing."""
        # Claude 3.5 Sonnet: $3/MTok input, $15/MTok output
        llm_cost_cents = (llm_tokens / 1_000_000) * 1500  # Average $15/MTok
        
        # OpenAI TTS: $15/1M characters
        tts_cost_cents = (tts_chars / 1_000_000) * 1500
        
        return {
            "llm_tokens": llm_tokens,
            "tts_chars": tts_chars,
            "llm_cost_cents": int(llm_cost_cents),
            "tts_cost_cents": int(tts_cost_cents),
            "total_cost_cents": int(llm_cost_cents + tts_cost_cents)
        }
```

Update estimate endpoint:
```python
# backend/api/routes/jobs.py
@router.post("/estimate", response_model=JobEstimate)
async def estimate_job(
    request: JobEstimateRequest,
    db: Session = Depends(get_db)
):
    """Estimate tokens and cost BEFORE creating job."""
    # 1. Parse repository to get file contents
    parse_result = await parse_repository(request.repo_url, request.git_ref)
    
    # 2. Filter by selected files
    selected_contents = filter_files(
        parse_result.files, 
        request.selected_files,
        request.excluded_patterns
    )
    
    # 3. Estimate tokens
    estimator = TokenEstimator()
    llm_tokens = estimator.estimate_llm_tokens(selected_contents)
    
    # Estimate script length (words per file)
    estimated_words = len(selected_contents) * 500  # 500 words per file average
    tts_chars = estimator.estimate_tts_tokens(estimated_words)
    
    # 4. Calculate costs
    cost_breakdown = estimator.calculate_cost(llm_tokens, tts_chars)
    
    return JobEstimate(**cost_breakdown, estimated_duration_minutes=len(selected_contents) * 3)
```

**Day 9-10: Build Cost Approval Gate**

Files to create:
- `src/pages/CostEstimate.tsx` — Show token count and cost breakdown
- `src/components/CostBreakdown.tsx` — Visual breakdown (LLM vs TTS)

```typescript
// src/pages/CostEstimate.tsx
export default function CostEstimate() {
  const { estimate } = useLocation().state; // From ScopeSelection
  const [approved, setApproved] = useState(false);
  
  const handleApprove = async () => {
    // Create job with user_approved_cost = true
    const job = await apiClient.createJob({
      ...jobData,
      user_approved_cost: true,
      estimated_total_tokens: estimate.llm_tokens + estimate.tts_chars
    });
    navigate(`/jobs/${job.id}`);
  };
  
  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1>Review Cost Estimate</h1>
      
      <CostBreakdown 
        llmTokens={estimate.llm_tokens}
        ttsChars={estimate.tts_chars}
        llmCostCents={estimate.llm_cost_cents}
        ttsCostCents={estimate.tts_cost_cents}
      />
      
      <div className="border-t pt-4 mt-4">
        <p className="text-2xl font-bold">
          Total: ${(estimate.total_cost_cents / 100).toFixed(2)}
        </p>
      </div>
      
      <Checkbox 
        checked={approved}
        onCheckedChange={setApproved}
        label="I approve this cost estimate and understand tokens will be spent"
      />
      
      <Button 
        onClick={handleApprove}
        disabled={!approved}
      >
        Approve and Continue to Payment
      </Button>
    </div>
  );
}
```

**Sprint 1 Deliverable:**
✅ Users can preview repository (README + file tree)  
✅ Users can select scope (files, language priority)  
✅ Users see real token estimates and costs  
✅ Users must explicitly approve before any tokens are spent  

---

## Sprint 2: Episode Architecture (3 weeks)

**Goal:** Shift from file-based chapters to relationship-based episodes

### Week 3: Episode Database Model

**Day 11-12: Create Episode Model**

Files to create:
- `backend/models/episode.py` — New Episode model

```python
# backend/models/episode.py
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Float, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.db.base import Base
import uuid
import enum

class EpisodeStatus(str, enum.Enum):
    PENDING = "pending"
    PLANNING = "planning"
    SCRIPTING = "scripting"
    SYNTHESIZING = "synthesizing"
    COMPLETED = "completed"
    FAILED = "failed"

class Episode(Base):
    __tablename__ = "episodes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    
    # Episode identity
    episode_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    narrative_theme = Column(Text, nullable=False)  # "How Authentication Works"
    
    # Relationship-based structure
    file_clusters = Column(JSONB)  # {"auth": ["auth.py", "middleware.py"], "models": ["user.py"]}
    dependency_graph = Column(JSONB)  # {"auth.py": ["user.py", "db.py"]}
    architectural_boundary = Column(String)  # "Authentication Layer", "Data Access Layer"
    
    # Dialogue planning
    conversation_hooks = Column(JSONB)  # ["Why use JWT?", "Trade-offs of stateless auth"]
    learning_objectives = Column(JSONB)  # ["Understand JWT flow", "Learn refresh token pattern"]
    
    # Generation metadata
    estimated_tokens = Column(Integer)
    status = Column(Enum(EpisodeStatus), default=EpisodeStatus.PENDING)
    
    # Output
    dialogue_script = Column(Text)  # Two-host conversation
    audio_url = Column(String)
    duration_seconds = Column(Integer)
    
    # Relationships
    # job = relationship("Job", back_populates="episodes")
```

Migration:
```bash
alembic revision -m "create_episodes_table"
alembic upgrade head
```

Update Job model:
```python
# backend/models/job.py
class Job(Base):
    # ... existing fields ...
    
    # Add episode count tracking
    estimated_episodes = Column(Integer)  # Replaces estimated_chapters
    # episodes = relationship("Episode", back_populates="job")
```

### Week 4-5: Dependency Analysis & Episode Planning

**Day 13-17: Build Dependency Analyzer**

Files to create:
- `backend/services/dependency_analyzer.py` — Extract import graphs

```python
# backend/services/dependency_analyzer.py
from typing import Dict, List, Set
import ast
from pathlib import Path

class DependencyAnalyzer:
    def __init__(self, repo_path: str, primary_language: str):
        self.repo_path = Path(repo_path)
        self.primary_language = primary_language
        self.import_graph = {}
    
    def analyze_python_imports(self, file_path: Path) -> List[str]:
        """Extract imports from Python file."""
        with open(file_path) as f:
            tree = ast.parse(f.read())
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        return imports
    
    def build_dependency_graph(self, files: List[str]) -> Dict[str, List[str]]:
        """Build complete dependency graph for repository."""
        graph = {}
        
        for file_path in files:
            if file_path.endswith('.py'):
                imports = self.analyze_python_imports(Path(self.repo_path) / file_path)
                graph[file_path] = imports
            # TODO: Add JavaScript/TypeScript analysis with ts-morph
        
        return graph
    
    def cluster_related_files(self, graph: Dict) -> List[Set[str]]:
        """Group files into clusters based on dependencies."""
        # Use graph clustering algorithm (e.g., connected components)
        clusters = []
        visited = set()
        
        def dfs(file: str, cluster: Set[str]):
            if file in visited:
                return
            visited.add(file)
            cluster.add(file)
            for dep in graph.get(file, []):
                dfs(dep, cluster)
        
        for file in graph:
            if file not in visited:
                cluster = set()
                dfs(file, cluster)
                clusters.append(cluster)
        
        return clusters
    
    def identify_architectural_layers(self, clusters: List[Set[str]]) -> Dict:
        """Identify layers like 'Data Access', 'Business Logic', 'API'."""
        layers = {}
        
        for cluster in clusters:
            # Heuristic: Files in 'models/' = Data Access
            if any('models/' in f or 'db/' in f for f in cluster):
                layers['Data Access Layer'] = cluster
            elif any('api/' in f or 'routes/' in f for f in cluster):
                layers['API Layer'] = cluster
            elif any('services/' in f or 'business/' in f for f in cluster):
                layers['Business Logic Layer'] = cluster
        
        return layers
```

**Day 18-22: Rewrite OutlineGenerator for Episodes**

Files to modify:
- `backend/agents/outline_agent.py` — Episode-based planning

```python
# backend/agents/outline_agent.py
async def create_outline_agent(chat_client, settings):
    return Agent(
        name="EpisodeOutlineGenerator",
        instructions="""
        You are an expert technical educator creating podcast episodes about codebases.
        
        Your goal: Plan THEMATIC EPISODES based on architectural relationships, not files.
        
        Input:
        - Repository analysis (file structure, dependency graph)
        - File clusters (groups of related files)
        - Architectural layers (API, business logic, data access)
        
        Output JSON:
        {
          "episodes": [
            {
              "number": 1,
              "title": "Authentication Deep Dive",
              "narrative_theme": "How JWT authentication flows through the system",
              "file_clusters": {
                "auth_core": ["auth.py", "jwt_utils.py"],
                "middleware": ["auth_middleware.py"],
                "models": ["user.py"]
              },
              "dependency_graph": {
                "auth.py": ["jwt_utils.py", "user.py"],
                "auth_middleware.py": ["auth.py"]
              },
              "architectural_boundary": "Authentication Layer",
              "conversation_hooks": [
                "Why use JWT over session cookies?",
                "How does refresh token rotation work?",
                "What happens when a token expires during a request?"
              ],
              "learning_objectives": [
                "Understand JWT validation flow",
                "Learn refresh token best practices",
                "Grasp middleware request lifecycle"
              ],
              "estimated_duration_minutes": 25
            }
          ],
          "total_episodes": 8,
          "total_duration_minutes": 180,
          "narrative_arc": "Start with entry points (API routes), dive into business logic, end with data persistence"
        }
        
        RULES:
        1. Episodes should tell a STORY, not list files
        2. Group files by RELATIONSHIPS, not directory structure
        3. Each episode needs CONVERSATION HOOKS for two-host dialogue
        4. Target 20-30 minutes per episode (not too short, not too long)
        5. Build a narrative arc across episodes (beginning → middle → end)
        """,
        chat_client=chat_client,
        tools=[
            dependency_analysis_tool,
            file_clustering_tool,
            architectural_layer_tool
        ]
    )
```

Update workflow:
```python
# backend/workflows/audiobook_workflow.py
async def run_outline_generation(job_id: str, db: Session):
    job = db.query(Job).get(job_id)
    
    # 1. Analyze dependencies
    analyzer = DependencyAnalyzer(job.repo_path, job.primary_language)
    dep_graph = analyzer.build_dependency_graph(job.selected_files)
    clusters = analyzer.cluster_related_files(dep_graph)
    layers = analyzer.identify_architectural_layers(clusters)
    
    # 2. Generate episode outline
    agent = await create_outline_agent(chat_client, settings)
    result = await agent.run({
        "dependency_graph": dep_graph,
        "file_clusters": clusters,
        "architectural_layers": layers,
        "depth_tier": job.depth_tier
    })
    
    # 3. Create Episode records
    outline_data = json.loads(result.content)
    for ep in outline_data['episodes']:
        episode = Episode(
            job_id=job.id,
            episode_number=ep['number'],
            title=ep['title'],
            narrative_theme=ep['narrative_theme'],
            file_clusters=ep['file_clusters'],
            dependency_graph=ep['dependency_graph'],
            architectural_boundary=ep.get('architectural_boundary'),
            conversation_hooks=ep['conversation_hooks'],
            learning_objectives=ep['learning_objectives'],
            estimated_tokens=ep.get('estimated_tokens', 10000)
        )
        db.add(episode)
    
    db.commit()
```

### Week 5: Frontend for Episodes

**Day 23-25: Update Outline Preview**

Files to create:
- `src/pages/EpisodeOutlinePreview.tsx` — Replace OutlinePreview.tsx
- `src/components/DependencyGraph.tsx` — Visual dependency visualization

```typescript
// src/pages/EpisodeOutlinePreview.tsx
export default function EpisodeOutlinePreview() {
  const { jobId } = useParams();
  const { data: episodes, isLoading } = useQuery({
    queryKey: ['episodes', jobId],
    queryFn: () => apiClient.getJobEpisodes(jobId)
  });
  
  return (
    <div className="max-w-6xl mx-auto p-8">
      <h1>Episode Outline for Review</h1>
      
      <div className="mb-6">
        <p className="text-muted-foreground">
          We've planned {episodes?.length} thematic episodes based on 
          architectural relationships in your codebase.
        </p>
      </div>
      
      {episodes?.map(episode => (
        <Card key={episode.id} className="mb-4">
          <CardHeader>
            <CardTitle>
              Episode {episode.episode_number}: {episode.title}
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              {episode.narrative_theme}
            </p>
          </CardHeader>
          
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-2">File Clusters</h4>
                {Object.entries(episode.file_clusters).map(([cluster, files]) => (
                  <div key={cluster} className="mb-2">
                    <Badge>{cluster}</Badge>
                    <ul className="text-sm ml-4 mt-1">
                      {files.map(f => <li key={f}>{f}</li>)}
                    </ul>
                  </div>
                ))}
              </div>
              
              <div>
                <h4 className="font-semibold mb-2">Conversation Topics</h4>
                <ul className="text-sm space-y-1">
                  {episode.conversation_hooks.map((hook, i) => (
                    <li key={i}>💬 {hook}</li>
                  ))}
                </ul>
              </div>
            </div>
            
            <div className="mt-4">
              <DependencyGraph graph={episode.dependency_graph} />
            </div>
          </CardContent>
        </Card>
      ))}
      
      <Button onClick={handleApprove} size="lg">
        Approve Episode Structure & Continue to Payment
      </Button>
    </div>
  );
}
```

**Sprint 2 Deliverable:**
✅ Episode model replaces Chapter model  
✅ Dependency analysis identifies relationships  
✅ Outline generator plans thematic episodes  
✅ Frontend shows episode structure with dependencies  

---

## Sprint 3: Podcast Dialogue Generation (3 weeks)

**Goal:** Transform from single-narrator scripts to two-host podcast conversations

### Week 6: Host Persona System

**Day 26-27: Design Host Personas**

Files to create:
- `backend/agents/personas.py` — Host character definitions

```python
# backend/agents/personas.py
from dataclasses import dataclass
from typing import List

@dataclass
class HostPersona:
    name: str
    role: str
    personality: str
    knowledge_level: str
    speaking_style: str
    system_prompt: str

# Define two default personas
SENIOR_DEV_PERSONA = HostPersona(
    name="Alex",
    role="Senior Software Engineer",
    personality="Experienced, patient, explains complex concepts clearly",
    knowledge_level="Expert in system design and architecture",
    speaking_style="Conversational but technical, uses analogies",
    system_prompt="""
    You are Alex, a senior software engineer with 10+ years of experience.
    
    Your role in this podcast: Guide the listener through the codebase's architecture.
    
    Speaking style:
    - Explain WHY design decisions were made, not just WHAT the code does
    - Use analogies to make complex concepts accessible
    - Anticipate questions the listener might have
    - Point out trade-offs and alternatives
    
    When your co-host asks questions:
    - Answer thoroughly but concisely
    - Build on their curiosity to explore deeper topics
    - Encourage their learning journey
    
    Example dialogue:
    "So, you might be wondering why they chose JWT over sessions here. 
    Let me break down the trade-offs..."
    """
)

CURIOUS_LEARNER_PERSONA = HostPersona(
    name="Jamie",
    role="Junior Developer / Curious Learner",
    personality="Enthusiastic, asks clarifying questions, represents the listener",
    knowledge_level="Intermediate, eager to learn",
    speaking_style="Curious, asks 'why' questions, seeks practical understanding",
    system_prompt="""
    You are Jamie, a developer with 2-3 years of experience who's eager to learn.
    
    Your role in this podcast: Ask the questions listeners would ask.
    
    Speaking style:
    - Ask WHY and HOW questions naturally
    - Seek practical understanding ("How would this help in production?")
    - Request clarification when concepts get complex
    - Connect new concepts to familiar patterns
    
    When reviewing code:
    - Express genuine curiosity
    - Ask about edge cases and real-world scenarios
    - Help Alex elaborate on important points
    
    Example dialogue:
    "That's interesting! But what happens if the token expires while 
    a user is in the middle of a long operation? How does the system handle that?"
    """
)
```

### Week 7-8: Dialogue Script Generation

**Day 28-35: Rewrite ScriptWriter for Conversations**

Files to modify:
- `backend/agents/script_agent.py` — Two-host dialogue generation

```python
# backend/agents/script_agent.py
from backend.agents.personas import SENIOR_DEV_PERSONA, CURIOUS_LEARNER_PERSONA

async def create_dialogue_agent(chat_client, settings):
    return Agent(
        name="PodcastDialogueWriter",
        instructions="""
        You are a podcast dialogue writer creating conversations between two hosts.
        
        Hosts:
        - Alex (Senior Dev): Technical expert, explains architecture
        - Jamie (Curious Learner): Asks questions listeners would ask
        
        Input:
        - Episode narrative theme
        - File clusters with code snippets
        - Conversation hooks (questions to explore)
        - Learning objectives
        
        Output Format (DIALOGUE SCRIPT):
        ```
        [INTRO]
        Alex: Welcome back! Today we're diving into the authentication layer 
              of this codebase. Jamie, what caught your eye here?
        
        Jamie: Well, I noticed they're using JWT tokens instead of sessions. 
               I'm curious why they made that choice.
        
        Alex: Great question! Let me show you the trade-offs. If we look at 
              auth.py on line 42, you'll see the validate_token function...
        
        [CODE WALKTHROUGH]
        Alex: So here's how the flow works. When a user logs in, we generate 
              a JWT that contains their user ID and permissions.
        
        Jamie: Got it. But what happens if someone steals the token? How do 
               we invalidate it?
        
        Alex: Ah, you've hit on one of the key challenges with JWTs! Unlike 
              sessions, you can't just delete them from a database. Let me 
              show you how they handle refresh token rotation...
        
        [DISCUSSION]
        Jamie: This is really clever! I see why they chose this approach for 
               a stateless API. But wouldn't sessions be simpler?
        
        Alex: You're right that sessions are simpler in some ways. The trade-off 
              is scalability. Let me explain why...
        
        [CONCLUSION]
        Alex: So to wrap up, we've seen how JWT authentication flows through 
              the middleware, validation, and refresh logic.
        
        Jamie: And we learned why they chose stateless auth for horizontal 
               scaling. That makes so much sense now!
        ```
        
        RULES:
        1. Natural back-and-forth (not scripted Q&A)
        2. Jamie asks questions at natural points
        3. Alex provides context before diving into code
        4. Reference specific files/lines when discussing code
        5. Build narrative momentum (beginning → insight → conclusion)
        6. Target 2500-3500 words (20-25 minute episode)
        7. Use conversation hooks from episode outline
        8. Achieve learning objectives through dialogue
        """,
        chat_client=chat_client,
        tools=[
            code_snippet_retrieval_tool,
            symbol_lookup_tool,
            dependency_graph_tool
        ]
    )

async def generate_episode_dialogue(episode: Episode, db: Session) -> str:
    """Generate two-host dialogue for an episode."""
    
    # 1. Retrieve code context for episode
    code_context = await retrieve_code_for_clusters(
        episode.file_clusters,
        episode.dependency_graph
    )
    
    # 2. Create dialogue agent
    agent = await create_dialogue_agent(chat_client, settings)
    
    # 3. Generate conversation
    result = await agent.run({
        "narrative_theme": episode.narrative_theme,
        "file_clusters": episode.file_clusters,
        "code_context": code_context,
        "conversation_hooks": episode.conversation_hooks,
        "learning_objectives": episode.learning_objectives,
        "senior_dev_persona": SENIOR_DEV_PERSONA.system_prompt,
        "learner_persona": CURIOUS_LEARNER_PERSONA.system_prompt
    })
    
    # 4. Parse dialogue script
    dialogue_script = result.content
    
    # 5. Save to episode
    episode.dialogue_script = dialogue_script
    db.commit()
    
    return dialogue_script
```

**Day 36-38: Implement Turn-Taking Logic**

Files to create:
- `backend/services/dialogue_parser.py` — Parse speaker turns

```python
# backend/services/dialogue_parser.py
import re
from typing import List, Tuple

class DialogueParser:
    def parse_script(self, dialogue_script: str) -> List[Tuple[str, str]]:
        """
        Parse dialogue script into (speaker, text) tuples.
        
        Returns:
        [
          ("Alex", "Welcome back! Today we're diving into..."),
          ("Jamie", "Well, I noticed they're using JWT tokens..."),
          ...
        ]
        """
        turns = []
        pattern = r'^(Alex|Jamie):\s*(.+)$'
        
        for line in dialogue_script.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                speaker, text = match.groups()
                turns.append((speaker, text.strip()))
        
        return turns
    
    def validate_dialogue(self, turns: List[Tuple[str, str]]) -> bool:
        """Ensure dialogue alternates speakers and has proper flow."""
        if not turns:
            return False
        
        # Check for reasonable turn length
        if len(turns) < 10:
            return False
        
        # Check for turn-taking (not one speaker dominating)
        speaker_counts = {"Alex": 0, "Jamie": 0}
        for speaker, _ in turns:
            speaker_counts[speaker] += 1
        
        # Jamie should speak at least 30% of the time
        jamie_ratio = speaker_counts["Jamie"] / len(turns)
        if jamie_ratio < 0.3:
            return False
        
        return True
```

### Week 8-9: Dual-Voice Audio Synthesis

**Day 39-43: Implement Two-Voice TTS**

Files to modify:
- `backend/services/audio_synthesizer.py` — Dual-voice synthesis

```python
# backend/services/audio_synthesizer.py
from openai import AsyncOpenAI
from pydub import AudioSegment
from backend.services.dialogue_parser import DialogueParser
import tempfile
import os

class DualVoiceSynthesizer:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.parser = DialogueParser()
        
        # Voice mappings
        self.voices = {
            "Alex": "onyx",    # Deeper, authoritative voice
            "Jamie": "nova"    # Lighter, curious voice
        }
    
    async def synthesize_dialogue(self, dialogue_script: str) -> str:
        """
        Synthesize two-host dialogue with distinct voices.
        
        Returns: Path to final merged audio file
        """
        # 1. Parse dialogue into turns
        turns = self.parser.parse_script(dialogue_script)
        
        # 2. Validate dialogue structure
        if not self.parser.validate_dialogue(turns):
            raise ValueError("Invalid dialogue structure")
        
        # 3. Synthesize each turn separately
        turn_audio_files = []
        for speaker, text in turns:
            audio_file = await self.synthesize_turn(speaker, text)
            turn_audio_files.append(audio_file)
        
        # 4. Merge turns with pauses
        final_audio = self.merge_turns(turn_audio_files)
        
        return final_audio
    
    async def synthesize_turn(self, speaker: str, text: str) -> str:
        """Synthesize single speaker turn."""
        voice = self.voices.get(speaker, "alloy")
        
        response = await self.client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=text,
            speed=1.0
        )
        
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_file.write(response.content)
        temp_file.close()
        
        return temp_file.name
    
    def merge_turns(self, audio_files: List[str]) -> str:
        """Merge individual turns into cohesive conversation."""
        # Start with silence
        combined = AudioSegment.silent(duration=500)  # 0.5s intro silence
        
        for i, audio_file in enumerate(audio_files):
            # Load turn audio
            turn_audio = AudioSegment.from_mp3(audio_file)
            
            # Add turn to combined audio
            combined += turn_audio
            
            # Add pause between turns (longer after questions)
            if i < len(audio_files) - 1:
                pause_duration = 800 if "?" in audio_file else 500
                combined += AudioSegment.silent(duration=pause_duration)
            
            # Clean up temp file
            os.remove(audio_file)
        
        # Add outro silence
        combined += AudioSegment.silent(duration=1000)
        
        # Export final audio
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        combined.export(output_file.name, format="mp3", bitrate="128k")
        
        return output_file.name
```

**Day 44-46: Update Player UI for Dialogue**

Files to modify:
- `src/pages/Player.tsx` — Show speaker labels
- `src/components/TranscriptViewer.tsx` — Display dialogue format

```typescript
// src/components/TranscriptViewer.tsx
export function TranscriptViewer({ episode }: { episode: Episode }) {
  const turns = parseDialogue(episode.dialogue_script);
  
  return (
    <div className="space-y-4">
      {turns.map((turn, i) => (
        <div 
          key={i}
          className={cn(
            "p-4 rounded-lg",
            turn.speaker === "Alex" 
              ? "bg-blue-50 dark:bg-blue-950" 
              : "bg-purple-50 dark:bg-purple-950"
          )}
        >
          <div className="flex items-center gap-2 mb-2">
            <Avatar>
              <AvatarFallback>
                {turn.speaker === "Alex" ? "AD" : "JL"}
              </AvatarFallback>
            </Avatar>
            <span className="font-semibold">{turn.speaker}</span>
          </div>
          
          <p className="text-sm">{turn.text}</p>
        </div>
      ))}
    </div>
  );
}

// Player.tsx - Show current speaker
export default function Player() {
  const [currentSpeaker, setCurrentSpeaker] = useState<string | null>(null);
  
  // Update speaker based on current timestamp
  useEffect(() => {
    const speaker = getCurrentSpeaker(audioRef.current?.currentTime);
    setCurrentSpeaker(speaker);
  }, [currentTime]);
  
  return (
    <div>
      <AudioPlayer ref={audioRef} src={episode.audio_url} />
      
      {currentSpeaker && (
        <div className="mt-4 flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm text-muted-foreground">
            {currentSpeaker} speaking
          </span>
        </div>
      )}
      
      <TranscriptViewer episode={episode} />
    </div>
  );
}
```

**Sprint 3 Deliverable:**
✅ Two host personas defined (Alex and Jamie)  
✅ Dialogue generation creates conversational scripts  
✅ Dual-voice TTS with distinct voices per speaker  
✅ Player UI shows speaker labels and turns  
✅ Output is podcast dialogue, not narration  

---

## Sprint 4: Queue System & Polish (1 week)

**Goal:** Production-ready workflow management and final integration

### Day 47-49: Job Queue System

Files to create:
- `backend/models/job_queue.py` — Queue model
- `backend/services/queue_manager.py` — Queue service

```python
# backend/models/job_queue.py
class JobQueue(Base):
    __tablename__ = "job_queue"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), unique=True)
    
    queue_position = Column(Integer, nullable=False)
    priority = Column(Integer, default=0)  # Higher = more urgent
    
    queued_at = Column(DateTime, default=datetime.utcnow)
    estimated_start_time = Column(DateTime)
    estimated_completion_time = Column(DateTime)
    
    status = Column(String, default="queued")  # queued, processing, completed

# backend/services/queue_manager.py
class QueueManager:
    def add_to_queue(self, job_id: str, priority: int = 0) -> int:
        """Add job to queue and return position."""
        position = db.query(JobQueue).count() + 1
        
        queue_entry = JobQueue(
            job_id=job_id,
            queue_position=position,
            priority=priority
        )
        db.add(queue_entry)
        db.commit()
        
        return position
    
    def get_next_job(self) -> Optional[Job]:
        """Get highest priority job from queue."""
        entry = db.query(JobQueue)\
            .filter(JobQueue.status == "queued")\
            .order_by(JobQueue.priority.desc(), JobQueue.queued_at)\
            .first()
        
        if entry:
            entry.status = "processing"
            db.commit()
            return entry.job
        
        return None
```

Files to create:
- `src/pages/Queue.tsx` — Queue visibility UI

```typescript
// src/pages/Queue.tsx
export default function Queue() {
  const { data: queueStatus } = useQuery({
    queryKey: ['queue'],
    queryFn: () => apiClient.getQueueStatus(),
    refetchInterval: 5000  // Poll every 5 seconds
  });
  
  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1>Job Queue</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Your Position: #{queueStatus?.position}</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Estimated start time: {queueStatus?.estimated_start}</p>
          <p>Jobs ahead: {queueStatus?.jobs_ahead}</p>
          
          <Progress value={queueStatus?.progress_percentage} />
        </CardContent>
      </Card>
    </div>
  );
}
```

### Day 50-51: Mixed Stack Handling

Files to modify:
- `backend/api/routes/parse.py` — Detect multiple languages

```python
# backend/api/routes/parse.py
@router.post("/repository")
async def parse_repository(request: ParseRequest):
    # ... existing parse logic ...
    
    # Detect languages
    languages = detect_languages(parse_result.files)
    
    return {
        "readme": readme_content,
        "file_tree": file_tree,
        "languages": languages,  # NEW: {"Python": 45, "TypeScript": 30, "Go": 25}
        "primary_language": max(languages, key=languages.get) if len(languages) == 1 else None,
        "is_mixed_stack": len(languages) > 1
    }
```

Files to create:
- `src/components/LanguagePrioritySelector.tsx` — User selects primary language

```typescript
// src/components/LanguagePrioritySelector.tsx
export function LanguagePrioritySelector({ 
  languages, 
  onSelect 
}: { 
  languages: Record<string, number>, 
  onSelect: (lang: string) => void 
}) {
  return (
    <div className="space-y-4">
      <h3>Multiple Languages Detected</h3>
      <p className="text-sm text-muted-foreground">
        Choose the primary language to focus the podcast on:
      </p>
      
      <RadioGroup onValueChange={onSelect}>
        {Object.entries(languages)
          .sort(([, a], [, b]) => b - a)
          .map(([lang, percentage]) => (
            <div key={lang} className="flex items-center space-x-2">
              <RadioGroupItem value={lang} id={lang} />
              <Label htmlFor={lang}>
                {lang} ({percentage}% of codebase)
              </Label>
            </div>
          ))}
      </RadioGroup>
    </div>
  );
}
```

### Day 52-53: Final Integration & Testing

1. End-to-end flow testing
2. Cost calculation verification
3. Episode generation quality checks
4. Dialogue synthesis testing
5. Queue system stress testing

**Sprint 4 Deliverable:**
✅ Job queue with position tracking  
✅ Mixed stack language selection  
✅ End-to-end integration complete  
✅ Production-ready system  

---

## Database Migration Summary

**New Tables:**
1. `episodes` — Replaces chapter-based structure
2. `job_queue` — Queue management
3. `scope_approvals` — Track user scope selections

**Updated Tables:**
1. `jobs` — Add scope selection, token estimation, queue fields
2. `users` — (No changes needed)

**Migration Order:**
```bash
# 1. Add scope fields to jobs
alembic revision -m "add_scope_selection_to_jobs"

# 2. Create episodes table
alembic revision -m "create_episodes_table"

# 3. Create job queue
alembic revision -m "create_job_queue_table"

# 4. Create scope approvals
alembic revision -m "create_scope_approvals_table"

# Apply all
alembic upgrade head
```

---

## API Changes Summary

**New Endpoints:**
- `POST /api/v1/parse/repository` — Pre-agent repository preview (already exists)
- `GET /api/v1/jobs/{id}/episodes` — Get episode outline
- `POST /api/v1/jobs/{id}/approve-scope` — Approve scope selection
- `POST /api/v1/jobs/{id}/approve-cost` — Approve cost estimate
- `GET /api/v1/queue/status` — Get queue position

**Modified Endpoints:**
- `POST /api/v1/jobs/estimate` — Now returns real token counts
- `POST /api/v1/jobs` — Accepts scope selection fields

---

## Open Questions for Team Discussion

### 1. Episode Granularity
**Question:** Should episodes target fixed duration (20-30 min) or variable length based on natural architectural boundaries?

**Options:**
- A) Fixed duration (easier to estimate, predictable listening)
- B) Variable length (more natural narrative flow, may be 10 min or 45 min)

**Recommendation:** Start with fixed duration for MVP, allow variable in future.

---

### 2. Cost Estimation Accuracy
**Question:** Show exact token counts or ranges to account for dialogue variability?

**Options:**
- A) Exact: "15,234 tokens = $22.85"
- B) Range: "14,000-17,000 tokens = $21-$26"
- C) Fixed price with buffer: "Standard tier = $49 (includes up to 20,000 tokens)"

**Recommendation:** Option C for MVP (predictable pricing), Option B for transparency.

---

### 3. Scope Selection Default Behavior
**Question:** Default to "include all" with opt-out, or require explicit file selection?

**Options:**
- A) Include all by default (faster onboarding, risk of large repos)
- B) Require explicit selection (safer, more friction)
- C) Smart defaults (include common patterns like src/, exclude node_modules/)

**Recommendation:** Option C with override.

---

### 4. Dialogue Voice Selection
**Question:** Hardcode two personas (Alex/Jamie) or allow user customization?

**Options:**
- A) Fixed personas (simpler, consistent quality)
- B) 3-4 preset styles ("Technical Deep Dive", "Beginner Friendly", "Architecture Review")
- C) Full customization (name, personality, voice)

**Recommendation:** Option A for MVP, Option B for differentiation.

---

### 5. Migration Strategy
**Question:** Support both chapter and episode models during transition?

**Options:**
- A) Hard cutover (deprecate chapters immediately)
- B) Dual mode (support both for 1-2 months)
- C) Migration script (convert existing chapter jobs to episodes)

**Recommendation:** Option A (clean break, episodes are fundamentally different).

---

## Success Metrics

**Sprint 1 Success:**
- [ ] Users can preview README and file tree before job creation
- [ ] Users can select scope (files, language priority)
- [ ] Real token estimates shown with cost breakdown
- [ ] 90%+ of users approve costs (trust signal)

**Sprint 2 Success:**
- [ ] Episodes planned based on architectural boundaries, not files
- [ ] Dependency graphs visible in outline preview
- [ ] Thematic episode titles (not "Chapter 1: auth.py")
- [ ] Conversation hooks generate meaningful dialogue prompts

**Sprint 3 Success:**
- [ ] Dialogue scripts have natural back-and-forth
- [ ] Two distinct voices in synthesized audio
- [ ] Player UI shows current speaker
- [ ] 80%+ of dialogue turns alternate between hosts

**Sprint 4 Success:**
- [ ] Queue shows accurate position and ETA
- [ ] Mixed stack repos handle language priority
- [ ] End-to-end flow from URL to podcast completes
- [ ] System scales to 10+ concurrent jobs

---

## Risk Mitigation

### Risk: Episode Planning Complexity
**Mitigation:**
- Start with simple clustering (directory-based)
- Gradually add dependency analysis
- Fallback to file-based if clustering fails

### Risk: Dialogue Quality
**Mitigation:**
- Extensive prompt engineering
- A/B test different conversation styles
- Manual review of first 10 episodes
- Iterate on persona system prompts

### Risk: Token Cost Explosion
**Mitigation:**
- Hard caps on tokens per job
- Conservative estimation (over-estimate by 20%)
- User approval required at cost gate
- Monitor actual vs estimated costs

### Risk: User Adoption of Scope Selector
**Mitigation:**
- Smart defaults (include common patterns)
- "Quick start" mode (auto-select recommended scope)
- Visual feedback on selection impact
- Tooltip guidance on best practices

---

## Implementation Checklist

### Sprint 1: Trust & Control
- [ ] Wire parse endpoint to Submit.tsx
- [ ] Create RepositoryPreview.tsx
- [ ] Build FileTreeSelector.tsx
- [ ] Add scope fields to Job model
- [ ] Implement TokenEstimator service
- [ ] Create CostEstimate.tsx
- [ ] Add cost approval gate to workflow

### Sprint 2: Episode Architecture
- [ ] Create Episode model and migration
- [ ] Build DependencyAnalyzer service
- [ ] Rewrite OutlineGenerator for episodes
- [ ] Update workflow for episode execution
- [ ] Create EpisodeOutlinePreview.tsx
- [ ] Add DependencyGraph visualization

### Sprint 3: Podcast Dialogue
- [ ] Define host personas (Alex, Jamie)
- [ ] Rewrite ScriptWriter for dialogue
- [ ] Implement DialogueParser
- [ ] Build DualVoiceSynthesizer
- [ ] Update Player.tsx for speaker labels
- [ ] Create TranscriptViewer.tsx

### Sprint 4: Queue & Polish
- [ ] Create JobQueue model
- [ ] Build QueueManager service
- [ ] Create Queue.tsx UI
- [ ] Implement language detection
- [ ] Add LanguagePrioritySelector.tsx
- [ ] End-to-end integration testing

---

**Revised Pricing Tiers:**

**Survey** - $19
- 3-5 episodes
- 15-25 min per episode
- 1-2 hour total audio
- High-level architectural overview

**Standard** - $39
- 6-10 episodes  
- 20-30 min per episode
- 2-5 hour total audio
- Deep architectural + implementation coverage

**Comprehensive** - $69
- 10-15 episodes
- 25-35 min per episode  
- 4-9 hour total audio
- Exhaustive analysis with patterns, edge cases, testing strategies

---

**1. Episode Granularity**
Variable length (15-35 min) based on architectural boundaries. Survey groups multiple modules per episode, Standard covers modules individually, Comprehensive dives into implementation patterns within modules. Natural breaks matter more than fixed duration.

**2. Cost Estimation Accuracy**
Fixed tier pricing ($19/$39/$69). Show preview: "This repo → 7 episodes estimated → Standard tier ($39)". If repo exceeds tier max (e.g., 12 episodes on Standard), prompt upgrade or let user exclude scope.

**3. Scope Selection UX**
Include all by default. For repos estimating above tier limits, require exclusions: "28 episodes detected → exclude test/ and docs/ folders to fit Standard tier, or upgrade to Comprehensive."

**4. Dialogue Voice Selection**
Hardcode: **Senior Architect** (big picture, tradeoffs, design philosophy) debates **Senior Fullstack Developer** (implementation reality, practical concerns, "but what about X?"). Different opinions create natural tension—makes technical content engaging.

**5. Migration Strategy**
Call them "episodes" throughout. If current code uses chapters, rename to episodes during migration. Episode = podcast episode = architectural segment. Clean terminology, no dual-mode.