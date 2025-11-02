# Git Repository to Podcast: Epic & User Stories

**Epic**: As a developer wanting to share knowledge about codebases, I need a system that transforms any Git repository into an engaging, technically accurate podcast that walks through the architecture and implementation details in a conversational format.

---

## Vision & Core Problem

Developers struggle to onboard to new codebases or share architectural decisions effectively. Documentation goes stale, and video walkthroughs require significant production effort. We're building a system that generates podcast-style deep dives into code repositories, creating natural conversations between two AI hosts that discuss the architecture, implementation patterns, and design decisions with full grounding in the actual source code.

The system must earn trust before spending resources. Users see exactly what we see—the README and file tree—before any AI processing begins. They explicitly approve scope and understand costs before generation starts. The output must be verifiable: every claim in the podcast should trace back to specific files and symbols in the codebase.

---

## Architectural Principles Driving This Design

**Plugin Architecture as Code**  
Plugins define capabilities—reading files, parsing ASTs, calling external services, performing semantic search. They live in source control, not databases, because we need deterministic behavior and code review. Each agent gets assigned only the minimal set of plugins it needs for its specific task. This creates a least-privilege security model and keeps individual agent contexts small and focused.

**Episode-First Thinking**  
The unit of work is an episode, not a file or folder. We plan episodes based on file relationships and architectural boundaries, then retrieve only the code needed for each episode. This keeps context windows manageable and creates natural narrative boundaries.

**Many Small Agents Over One Large Brain**  
Rather than feeding everything to a massive context window, we orchestrate specialized agents with narrow responsibilities. An agent that plans episodes doesn't need code retrieval tools. An agent that writes narrative doesn't need AST parsing. This approach keeps costs predictable, makes failures localized and fixable, and allows parallel processing.

**Hard Gates Prevent Runaway Costs**  
There are explicit approval gates: scope selection happens before planning, cost estimation happens before queueing, and verification happens before finalization. No tokens get spent without user awareness and consent.

---

## User Journey: From URL to Podcast

```mermaid
graph TD
    A[User enters GitHub URL] --> B[Phase A: Pre-Agent Parse]
    B --> C{README & Tree Displayed}
    C --> D[Phase B: User Selects Scope]
    D --> E{Mixed Stack Decision}
    E -->|Multiple Languages| F[User Chooses Primary Stack]
    E -->|Single Stack| G[Phase C: Token Estimation]
    F --> G
    G --> H{User Reviews Credits}
    H -->|Approve| I[Phase D: Queue Generation]
    H -->|Reject| D
    I --> J[Planning: Episode Structure]
    J --> K[Execution: Per-Episode Generation]
    K --> L[Verification Loop]
    L --> M[Audio Synthesis]
    M --> N[Package & Deliver]
    
    style B fill:#e1f5ff
    style D fill:#fff4e1
    style G fill:#ffe1e1
    style I fill:#e1ffe1
    style K fill:#f0e1ff
    style M fill:#ffe1f0
</thinking>

I've created a comprehensive user story document that transforms your technical plan into a narrative SCRUM format with flow diagrams.

[View your document](computer:///mnt/user-data/outputs/podcast-generation-user-story.md)

The document includes:

- **Epic and vision statement** that frames the business problem
- **Detailed user stories** for each phase with narrative flow, acceptance criteria, and the "why it matters"
- **Multiple Mermaid flow diagrams** showing the overall journey, episode generation pipeline, planning process, frontend screens, and plugin architecture
- **Architectural principles** explained in context of user needs
- **Open discussion questions** for your team to address
- **Success metrics** and implementation phase suggestions

Each user story is written from the user's perspective while including enough technical detail for engineering discussion. The flow charts visualize key decision points, data flows, and system boundaries.