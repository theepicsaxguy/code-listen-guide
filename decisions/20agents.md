Hybrid LLM–Static Analysis Pipeline for Code Documentation Narratives

Transforming a codebase into a coherent, engaging narrative requires separating parsing from storytelling.  In a naive pipeline, one might feed every source file into a large language model (LLM) sequentially.  This quickly hits token limits and wastes compute on repetitive parsing.  Instead, we use a hybrid architecture: a static analyzer (e.g. using AST parsing or a tool like chonkie) produces a normalized knowledge base of the code (AST trees, docstrings, metadata, dependency graphs), and specialized LLM agents operate on top of that structured data.  This decoupling means the LLMs no longer re-parse code but instead query concise, pre-computed summaries.  For example, Meta’s DocAgent first performs static AST analysis to build a dependency DAG, then lets specialized agents (Reader, Searcher, Writer, Verifier, Orchestrator) collaboratively generate documentation.  Similarly, IBM notes that larger context windows help LLMs understand long codebases, but even 128K tokens can be exceeded by real projects; hence indexing and structured context (rather than raw code streaming) is crucial.

Most low-level tasks – like building the AST, indexing functions and classes, and computing call graphs – are deterministic and done once up front by tools (the “chonkie parse”).  The LLM’s role is then purely compositional: synthesizing summaries, naming parts, verifying coherence, and adding narrative flair.  This aligns with emerging best practices: multi-agent pipelines have shown dramatic gains in creative tasks by assigning narrow roles to each agent.  For instance, IBM’s Martin Keen describes an “agentic stack” where a planner, character generator, scene writer, style enforcer and critic each handle one aspect of story generation.  Likewise, the ACL 2025 NexusSum framework uses a hierarchical sequence of LLM agents to summarize novels and screenplays, yielding state-of-the-art coherence gains.  In our domain, we treat the 20-agent layout as a production crew, not code analysts. chonkie (or equivalent AST analysis) is our “camera and microphones” – it captures the raw facts once. The agents then “shoot the scenes” of the documentary-style audio script. Context resides in a vault (a structured index or vector memory) and agents make targeted queries to it, avoiding token bloat.

Key Components:

chonkie / Static Analyzer:  Produces the “frozen truth” layer: ASTs, docstrings, metrics and a dependency graph for every file. chonkie is designed for diverse formats and offers a unified chonkieDocument JSON format, which can serve as a persistent knowledge base. This base context can be cached, indexed or placed in a vector DB.  For example, one RAG-based system indexes every code file into 1,000-token chunks and retrieves relevant snippets via HNSW search during documentation generation.  In our approach, we instead index structured summaries (JSON or databases of AST nodes) so that each agent retrieves exactly the facts it needs.

Agent Coordination:  An orchestration layer manages agent execution.  We assume shared memory or a retrieval index (not raw prompt chaining) for passing context.  The orchestration (Producer) ensures each agent runs in sequence and respects length/style constraints.


Proposed Agent Roles

We assign each agent a narrow, creative role in the narrative pipeline.  Together they turn the raw structure into an audio-script style explanation of the code.  Each agent queries the chonkie-derived knowledge base (the “Context Vault”), uses LLM reasoning only for creative or summarization tasks, and refrains from low-level parsing.  Below are 20 example roles (in execution order), with responsibilities:

1. Context Vault Agent: Maintains the structured code knowledge base (ASTs, docstrings, dependency graph) as provided by chonkie.  It does not generate text – it only answers queries.  Think of it as a read-only DB: when an agent asks “what functions does module X define?”, it retrieves the answer. (This mirrors DocAgent’s Navigator, which performs static AST parsing and constructs a dependency DAG for context.)


2. Script Director Agent: Uses the contextual index to decide the overall narrative arc.  It chooses the order of “episodes” (code sections or modules) and thematic focus.  For instance, it might identify major components and decide to introduce the core engine first, then follow with auxiliary features.  It treats the codebase like a multi-episode documentary, setting pacing and transitions.


3. Episode Storyboard Agent: Converts the chosen sections into scene structures.  Each episode (e.g. a Python module or class) is broken into a “setup”, “conflict”, and “resolution” if applicable.  The agent identifies story beats: e.g. “First, we’ll set up the initial state of the data, then show how the update loop processes it, finally conclude with the result.”  This keeps technical narrative engaging and coherent.


4. Characterizer Agent: Personifies code components by assigning them traits and roles.  For example, “The Parser wakes first to greet the incoming data” or “The Authenticator stands guard at the door of the API.”  These analogies give human flavor without altering facts.  (NexusSum’s multi-agent approach similarly standardizes narratives while preserving content.)


5. Humor Editor Agent: Injects light humor or witty asides to keep listeners engaged.  It might add a small joke when a component is particularly quirky (“Our little error handler starts chuckling nervously...”).  It must ensure jokes don’t contradict the facts.


6. Style Harmonizer Agent: Enforces a consistent voice, tense, and terminology across all agents’ outputs.  It harmonizes style so the final script doesn’t feel disjointed.  This is akin to IBM’s “Voice Style Agent” which applies a reference style to maintain consistency.


7. Accuracy Verifier Agent: Cross-checks narrative embellishments against the chonkie database.  Whenever a creative agent suggests a detail (like “the class sorts its inputs”), the verifier confirms it by looking at the AST or code summary.  If an agent has drifted from the truth, the verifier flags it.  (This provides the “no hallucination” guardrail; DocAgent’s Verifier and Searcher agents perform similar factual checks against the codebase.)


8. Humanizer Agent: Rewrites technical descriptions into everyday analogies or simpler language.  For example, it might turn “the DatabaseConnector queues queries” into “Think of this class as a receptionist at the data center.”  The goal is to explain complex logic in a way a non-expert can visualize.


9. Accessibility Agent: Simplifies jargon and clarifies acronyms.  It ensures that any specialist terms are either explained or avoided.  This helps make the final script understandable to listeners with varying backgrounds.


10. Continuity Agent: Tracks recurring themes and callbacks.  If Episode 1 introduced a “forgotten sprite” or a key class, this agent ensures later episodes refer back (“Remember that helper routine from Episode 1?”).  This maintains a throughline and rewards attentive listeners.


11. Emotion Mapper Agent: Decides where to add dramatic pacing or emphasis cues.  It might suggest a pause after a surprising revelation, or an excited tone when describing a critical section.  These cues help in eventual audio narration (though it doesn’t produce actual audio).


12. Dialogue Synthesizer Agent: Writes light dialogues or internal monologues for components if needed (“The API sighs, ‘Not another request?!’”).  This adds character interaction to break up expository text.


13. Visual Cue Agent: Inserts hints for future visuals (e.g. diagrams or highlight animations).  For example: “(Imagine a flowchart forming here: data → processor → output.)” or descriptions of a hypothetical screen or code snapshot.  This can guide illustrators or animators if the script is later turned into video.


14. Fact-Weaver Agent: Smoothly integrates concrete metrics or numbers into the narrative.  It might say “This class uses exactly 5 helper functions” or “Out of 10 modules, 3 handle user input.”  It pulls from chonkie’s metadata (line counts, dependencies, coverage stats) and frames them naturally.


15. Episode Narrator Agent: Takes each episode’s structured content (from the storyboard) and writes a polished monologue of a few paragraphs, weaving scene descriptions and character actions.  This agent transitions between scenes and makes the story flow.


16. Context Threader Agent: Bridges gaps between episodes.  It adds brief recaps or lead-ins so listeners who skip ahead won’t be lost.  For instance, “Earlier we met the Parser; now we follow it into the database.”  This ensures the story is coherent no matter where one starts.


17. Intensity Balancer Agent: Adjusts the narrative rhythm.  It slows down (“beats”) during complex algorithmic explanations and speeds up through boilerplate sections.  It may compress or expand text to maintain listener interest and keep overall length on target.


18. QA Agent (Senior Dev): Reviews the draft script with a critical eye.  It trims fluff, fixes any weak analogies, and ensures technical accuracy.  Essentially, it plays a skeptical senior engineer double-checking for errors or misleading statements.


19. AudioScript Formatter Agent: Optimizes the final text for text-to-speech.  It adds line breaks, punctuation, and emphasis markers so that a narrator (or TTS engine) can deliver it clearly.  It might insert “[pause]” or adjust sentence length for better audibility.


20. Producer/Orchestrator Agent: Oversees the whole pipeline.  It checks that each agent’s output is coherent and within length limits, then compiles the final script.  It may loop back to earlier agents if something is inconsistent (e.g. changing the Script Director’s plan and regenerating episodes).  In essence, it’s the project manager ensuring the final product meets specifications.



Each agent focuses on its niche, querying only the relevant chonkie-derived context and then generating or editing text.  This compartmentalization keeps token use low and comprehension high.  As DocAgent’s evaluation shows, processing code in dependency order and with specialized agents produces more complete and factual documentation. Similarly, in our system the Context Vault + Context Threader ensure that each part of the code is explained exactly once, and higher-level agents handle only the narrative “glue.”  In sum, this hybrid, agentic approach turns static code metadata into a human-like engineer’s tour of the code, rather than forcing a single LLM to read raw source files sequentially.

Assumptions: chonkie (or similar) provides per-file summaries and dependency graphs; all agents share a retrieval index or memory; and the final goal is an audio-script style narrative.  Under these conditions, the architecture above maximizes consistency, creativity, and fidelity.

Sources: This design draws on recent advances in multi-agent LLM systems and code documentation.  For example, Meta’s DocAgent uses AST parsing and specialized LLM agents to generate high-quality code docs.  IBM’s Martin Keen similarly advocates a stack of narrative-focused agents (planner, character creator, critic, etc.) to overcome context window and style drift issues.  Studies like NexusSum also confirm that hierarchical multi-LLM pipelines excel at long-form narrative tasks.  Finally, practical tools illustrate the need for indexing: one open-source system chunks and vectorizes code files for retrieval, and IBM’s Granite models show that even very large context windows (128K tokens) are finite.  Our proposal unifies these insights: let chonkie/static analysis build the factual base once, and have a crew of LLM agents transform it into a coherent story.