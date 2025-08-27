# app/services/validator_questions.py
from __future__ import annotations
from typing import List, Tuple, Any
from app.models.ticket_agent import TicketPlan, MissingField, FieldDef
from app.services.catalog_service import find_ticket_spec, resolve_field_options

def _is_required(field_dict: dict) -> bool:
    """
    Decide if this field MUST be filled before "creating" the ticket.
    Convention: required defaults to True unless explicitly set to False in catalog.
    """
    return field_dict.get("required", True)

def find_missing_fields(plan: TicketPlan) -> List[MissingField]:
    """
    Compare each planned TicketItem against its TicketSpec (from catalog).
    If any required field isn't present or is empty, queue a MissingField.
    """
    print(f"🔍 VALIDATOR: Finding missing fields for {len(plan.items)} ticket items")
    missing: List[MissingField] = []
    for i, item in enumerate(plan.items):
        print(f"📋 VALIDATOR: Checking item {i}: {item.ticket_type}")
        spec = find_ticket_spec(item.service_area, item.category, item.ticket_type)
        if not spec:
            # If spec can't be found, it's a catalog mismatch—flag and skip questions.
            print(f"⚠️ VALIDATOR: No spec found for {item.ticket_type}, marking as needs-triage")
            item.labels = list(set(item.labels + ["needs-triage"]))
            continue

        print(f"📝 VALIDATOR: Found spec with {len(spec['fields'])} fields")
        for raw in spec["fields"]:
            fdef = FieldDef(**raw)  # normalize into our Pydantic FieldDef
            if not _is_required(raw):
                print(f"⏭️ VALIDATOR: Skipping optional field: {fdef.name}")
                continue  # optional field—skip if missing

            # Treat "", None, [] (for multi), {} (for rich objects) as missing
            value = item.form.get(fdef.name, None)
            is_blank = value in (None, "", [], {})
            if is_blank:
                print(f"❌ VALIDATOR: Missing required field: {fdef.name}")
                missing.append(MissingField(item_index=i, field=fdef))
            else:
                print(f"✅ VALIDATOR: Field {fdef.name} has value: {value}")

    print(f"📊 VALIDATOR: Found {len(missing)} missing fields total")
    return missing

def render_question(m: MissingField) -> dict:
    """
    Turn a MissingField into a question payload usable by your chatbot UI.
    Note: the "options" are resolved from constants.py if field.type is choice/multi_choice.
    """
    f = m.field
    # Human-friendly field display name (space out snake_case)
    nice = f.name.replace("_", " ").strip()

    # Basic prompt text per field type; you can tune copy here
    prompt_by_type = {
        "string"      : f'Please provide **{nice}**.',
        "rich_text"   : f'Add details for **{nice}** (you can include formatting and attach files).',
        "bool"        : f'Is **{nice}** true or false?',
        "int"         : f'Enter a number for **{nice}**.',
        "date"        : f'Pick a date for **{nice}**.',
        "time"        : f'Pick a time for **{nice}**.',
        "file"        : f'Upload a file for **{nice}**.',
        "files"       : f'Upload file(s) for **{nice}**.',
        "choice"      : f'Select **{nice}**.',
        "multi_choice": f'Select one or more options for **{nice}**.',
    }
    prompt_text = prompt_by_type.get(f.type, f'Provide **{nice}**.')

    # Resolve options for enumerated fields
    options = None
    if f.type in ("choice", "multi_choice"):
        options = resolve_field_options(f.model_dump())

    return {
        "text": prompt_text,
        "type": f.type,
        "options": options,                 # list or None
        "item_index": m.item_index,
        "field_name": f.name,
        "description": f.description or "", # UI can show this under the input
    }

def apply_answer(plan: TicketPlan, item_index: int, field_name: str, value: Any) -> TicketPlan:
    """
    Insert the user's answer into the right TicketItem.form slot.
    - For multi_choice, `value` must be a list[str].
    - For date/time, keep as ISO strings that your UI components produce.
    """
    plan.items[item_index].form[field_name] = value
    return plan
