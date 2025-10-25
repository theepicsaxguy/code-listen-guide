"""Agent helpers for the audiobook workflow."""

from typing import Any, Dict


def build_responses_client_options(settings: Any) -> Dict[str, Any]:
    """Return keyword arguments for constructing an OpenAI responses client."""

    api_key = getattr(settings, "openai_api_key", None)
    if not api_key:
        raise RuntimeError("OpenAI API key is not configured")
    options: Dict[str, Any] = {"api_key": api_key}
    model_id = getattr(settings, "openai_responses_model", None)
    if model_id:
        options["model_id"] = model_id
    base_url = getattr(settings, "openai_base_url", None)
    if base_url:
        options["base_url"] = base_url
    return options
