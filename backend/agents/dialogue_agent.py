"""Dialogue agent for generating two‑host podcast conversation scripts.

Uses Marcus (Architect) and Sara (Builder) personas to produce a
natural, educational back‑and‑forth grounded in episode metadata
and code context.

The agent returns a raw dialogue script text; parsing & validation
handled by services.dialogue_parser.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence, Dict

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIResponsesClient

from backend.agents.personas import ARCHITECT_PERSONA, FULLSTACK_PERSONA
from backend.agents.schemas import ScriptAgentResponse  # Reuse existing response schema if compatible
from . import build_responses_client_options


DIALOGUE_INSTRUCTIONS = f"""
You are orchestrating a technical podcast dialogue between two hosts:

Host A (Marcus Chen) Persona System Prompt:
{ARCHITECT_PERSONA.system_prompt}

Host B (Sara Okoye) Persona System Prompt:
{FULLSTACK_PERSONA.system_prompt}

TASK:
Generate a rich, engaging dialogue for the provided episode data.
The dialogue must:
 - Begin with Marcus framing architectural or thematic context (2-3 turns)
 - Transition to Sara exploring concrete code paths & edge cases
 - Include 2-3 productive disagreements or scrutiny moments (never hostile)
 - Reference specific files/functions (by name) when discussing implementation
 - Avoid dumping large code blocks; summarize logic verbally
 - Achieve learning objectives explicitly (Marcus: why / Sara: how / failure modes)
 - Conclude with Sara summarizing practical takeaways and Marcus summarizing architectural significance

FORMAT:
Plain text lines in order of speech. Each speaker line MUST start with
"Marcus:" or "Sara:" exactly (capitalized, colon, space). No other prefixes.
Include optional bracketed section markers for readability:
  [INTRO]
  [DEEP DIVE]
  [CHALLENGE]
  [RESOLUTION]
  [WRAP]

Do not include narration outside of speaker lines. Keep total length ~2500-3500 words.
Ensure ~35-55 turns; Sara should speak at least 35% of turns.

PROHIBITED:
 - Generic AI filler phrases ("It is worth noting", "In conclusion")
 - Overly formal academic tone
 - Large verbatim code listings

INPUT FIELDS (JSON provided to you):
 - narrative_theme
 - file_clusters (mapping cluster -> list[file])
 - conversation_hooks (list[str])
 - learning_objectives (list[str])
 - dependency_graph (optional mapping file -> list[dep])
 - architectural_boundary (optional)
 - code_context_snippets (list[str]) limited curated snippets

Incorporate conversation_hooks organically as questions Sara asks or Marcus anticipates.
Reference learning_objectives explicitly via explanation without listing them bluntly.

OUTPUT:
Return ONLY the dialogue text following the specified format.
""".strip()


async def create_dialogue_agent(
    chat_client: Any,
    *,
    tools: Optional[Sequence[Any]] = None,
    response_format: Any = ScriptAgentResponse,
) -> ChatAgent:
    return chat_client.create_agent(
        name="PodcastDialogueWriter",
        instructions=DIALOGUE_INSTRUCTIONS,
        tools=list(tools) if tools else [],
        response_format=response_format,
    )


async def dialogue_agent(settings: Any, *, tools: Optional[Sequence[Any]] = None) -> ChatAgent:
    client = OpenAIResponsesClient(**build_responses_client_options(settings))
    return await create_dialogue_agent(client, tools=tools)


async def generate_dialogue(
    agent: ChatAgent,
    episode_payload: Dict[str, Any],
) -> str:
    """Run the dialogue agent on episode payload; return raw script text.

    episode_payload should already limit included code to curated snippets
    for token efficiency. The agent returns a ScriptAgentResponse whose
    .content (or .raw) holds the text.
    """
    result = await agent.run(input=episode_payload)
    # Adapt depending on response_format; assume .content text
    content = getattr(result, "content", None) or getattr(result, "raw", "")
    return content

__all__ = [
    "create_dialogue_agent",
    "dialogue_agent",
    "generate_dialogue",
]
