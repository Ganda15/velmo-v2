"""Versionnage de l'agent : empreinte de la config (prompt + memoire + garde-fous)."""

from __future__ import annotations

import hashlib
import json

from velmo.agent import SYSTEM_PROMPT
from velmo.guardrails import CATEGORIES, GuardrailEngine
from velmo.memory import MemoryManager


def _config_snapshot() -> dict:
    """Photographie la configuration actuelle de l'agent."""
    memory = MemoryManager()
    return {
        "prompt": SYSTEM_PROMPT,
        "memory": {"token_budget": memory.token_budget},
        "guardrails": {
            "categories": sorted(CATEGORIES),
            "input_keywords": {
                category: sorted(keywords)
                for category, keywords in sorted(GuardrailEngine.INPUT_KEYWORDS.items())
            },
        },
    }


def version_id(snapshot: dict) -> str:
    """Transforme la photo de config en identifiant court et stable."""
    payload = json.dumps(snapshot, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"v-{digest[:12]}"
