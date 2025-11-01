from __future__ import annotations

import copy
from typing import Any, Callable, Dict, Mapping, MutableMapping, Optional

from agent_framework import AIFunction
from pydantic import BaseModel

from backend.workflows.dynamic_loader import ToolDescriptor


RegistryContract = Dict[str, Any]


def _as_object_schema(schema: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    if not isinstance(schema, Mapping):
        return {"type": "object", "properties": {}}
    normalized: Dict[str, Any] = {"type": "object", "properties": {}}
    source_type = schema.get("type")
    if isinstance(source_type, str) and source_type.lower() == "array":
        normalized["type"] = "object"
    if isinstance(schema.get("description"), str):
        normalized["description"] = schema["description"].strip()
    properties = schema.get("properties")
    if isinstance(properties, Mapping):
        normalized_props: Dict[str, Any] = {}
        for key, value in properties.items():
            key_text = str(key)
            if not isinstance(value, Mapping):
                normalized_props[key_text] = {"type": "string"}
                continue
            normalized_props[key_text] = copy.deepcopy(value)
        normalized["properties"] = normalized_props
    required = schema.get("required")
    if isinstance(required, (list, tuple)):
        required_names = [str(item) for item in required if str(item)]
        if required_names:
            normalized["required"] = required_names
    if "required" not in normalized:
        normalized.pop("required", None)
    return normalized


def _sanitize_schema(schema: Optional[Mapping[str, Any]]) -> Optional[Dict[str, Any]]:
    if not isinstance(schema, Mapping):
        return None
    cleaned = copy.deepcopy(dict(schema))
    if not cleaned:
        return None
    return cleaned


def build_function_contract(descriptor: ToolDescriptor) -> RegistryContract:
    parameters = _as_object_schema(descriptor.input_schema)
    returns = _sanitize_schema(descriptor.output_schema)
    metadata: Dict[str, Any] = {
        "registry_id": str(descriptor.id),
        "module_path": descriptor.module_path,
        "function_name": descriptor.function_name,
    }
    if descriptor.description_version:
        metadata["description_version"] = descriptor.description_version
    contract: RegistryContract = {
        "type": "function",
        "version": descriptor.description_version,
        "function": {
            "name": descriptor.name,
            "description": descriptor.description or "",
            "parameters": parameters,
            "metadata": metadata,
        },
    }
    if returns:
        contract["function"]["returns"] = returns
    return contract


class RegistryAIFunction(AIFunction[BaseModel, Any]):
    def __init__(
        self,
        *,
        func: Callable[..., Any],
        contract: RegistryContract,
        additional_properties: Optional[MutableMapping[str, Any]] = None,
    ) -> None:
        registry_properties: Dict[str, Any] = {"registry_contract": contract}
        if additional_properties:
            registry_properties.update(additional_properties)
        super().__init__(
            name=contract["function"]["name"],
            description=contract["function"]["description"],
            func=func,
            input_model=contract["function"]["parameters"],
            additional_properties=registry_properties,
        )
        self._contract = contract

    def to_json_schema_spec(self) -> Dict[str, Any]:
        function_spec: Dict[str, Any] = {
            "type": "function",
            "function": {
                "name": self._contract["function"]["name"],
                "description": self._contract["function"]["description"],
                "parameters": self._contract["function"]["parameters"],
            },
        }
        returns_schema = self._contract["function"].get("returns")
        if returns_schema:
            function_spec["function"]["returns"] = returns_schema
        metadata = self._contract["function"].get("metadata")
        if metadata:
            function_spec["function"]["metadata"] = metadata
        version = self._contract.get("version")
        if version:
            metadata_block = function_spec["function"].setdefault("metadata", {})
            metadata_block["description_version"] = version
        return function_spec


def build_registry_tool(
    descriptor: ToolDescriptor,
    handler: Callable[..., Any],
    *,
    additional_properties: Optional[MutableMapping[str, Any]] = None,
) -> RegistryAIFunction:
    contract = build_function_contract(descriptor)
    return RegistryAIFunction(
        func=handler,
        contract=contract,
        additional_properties=additional_properties,
    )
