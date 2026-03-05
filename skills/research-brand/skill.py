"""
research-brand skill
Queries Perplexica API to discover the official Singapore legal entity name
for a given brand.
"""
import json
from typing import Any, Dict

import requests


def execute(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Research a brand via the Perplexica search API and return the
    most likely Singapore corporate entity name.

    Args:
        inputs: dict with keys 'brand' (required) and optionally
                'perplexica_endpoint' (default http://localhost:3000).

    Returns:
        dict with 'entity_name' and 'research_summary'.
    """
    brand = inputs.get("brand", "")
    endpoint = inputs.get("perplexica_endpoint", "http://localhost:3000")

    if not brand:
        return {
            "status": "error",
            "message": "No brand name provided",
        }

    query = f"Singapore corporate legal entity official name for {brand}"

    try:
        response = requests.post(
            f"{endpoint}/api/search",
            json={
                "query": query,
                "focusMode": "webSearch",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()

        # Extract the answer / message returned by Perplexica
        answer = data.get("message", data.get("answer", ""))

        # Heuristic: first line often contains the entity name
        entity_name = _extract_entity_name(answer, brand)

        return {
            "entity_name": entity_name,
            "research_summary": answer,
        }

    except requests.ConnectionError:
        return {
            "status": "error",
            "message": f"Could not connect to Perplexica at {endpoint}. Is it running?",
        }
    except requests.Timeout:
        return {
            "status": "error",
            "message": "Perplexica request timed out",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Research failed: {str(e)}",
        }


def _extract_entity_name(text: str, fallback: str) -> str:
    """Best-effort extraction of a 'Pte Ltd' style entity name from text."""
    if not text:
        return fallback

    for line in text.split("\n"):
        line = line.strip()
        if "Pte" in line or "Ltd" in line or "PTE" in line:
            # Return the first line that looks like a legal entity name
            return line.strip("*•- ").split(".")[0].strip()

    # If nothing obvious, just return the original brand as-is
    return fallback
