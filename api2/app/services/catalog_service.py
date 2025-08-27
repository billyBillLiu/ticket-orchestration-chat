# app/services/catalog_service.py
from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel
from app.catalog import CATALOG

def get_service_area_categories() -> Dict[str, Dict[str, list]]:
    """
    Returns the 'categories' dict from your catalog so we can navigate:
    { "SRE/Production Support": { "IT Service Requests": [...], ... }, ... }
    """
    return CATALOG["categories"]

def find_ticket_spec(service_area: str, category: str, ticket_type: str) -> Optional[dict]:
    """
    Returns the raw spec dict for a ticket type:
    {
      "ticket_type": "...",
      "description": "...",
      "fields": [ {name,type,options/options_source, ... }, ... ]
    }
    """
    cats = get_service_area_categories()
    if service_area not in cats:
        return None
    if category not in cats[service_area]:
        return None
    for spec in cats[service_area][category]:
        if spec["ticket_type"] == ticket_type:
            return spec
    return None

def resolve_field_options(field_dict: dict) -> List[str]:
    """
    Given a field definition, return its choice list.
    - Returns the "options" list if present.
    - If no options, return [].
    """
    if "options" in field_dict and isinstance(field_dict["options"], list):
        return field_dict["options"]
    return []

def slice_catalog_for_prompt(user_text: str) -> dict:
    """
    Return a smaller chunk of the catalog based on naive keywords in the
    user's message so the LLM has fewer irrelevant choices.
    You can replace this with a smarter first-pass LLM classifier later.
    """
    cats = get_service_area_categories()
    focus_area = "SRE/Production Support"   # start here since that's where your examples are
    area_block = cats.get(focus_area, {})
    likely = {}

    keywords = {
        "datadog": "IT Service Requests",
        "sftp": "IT Service Requests",
        "yaml": "IT Service Requests",
        "jams": "IT Service Requests",
        "incident": "Report an Incident",
        "loan": "Financial Service Request",
        "investor": "Financial Service Request",
        "rerun": "Financial Service Request",
    }

    chosen = {cat for kw, cat in keywords.items() if kw in user_text.lower()}
    if not chosen:
        # no hints—include all categories for this service area
        chosen = set(area_block.keys())

    for cat in chosen:
        if cat in area_block:
            # copy the list of ticket specs for this category
            likely[cat] = area_block[cat]

    # Output shape the planner prompt expects
    return {focus_area: likely}
