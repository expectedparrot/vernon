---
name: coop-publishing
description: Saving EDSL objects locally and publishing them to Coop (Expected Parrot's servers).
---

# Saving and Publishing to Coop

How to persist EDSL objects locally and share them via Coop (Expected Parrot's servers).
The object itself is defined in another Python file e.g.,
`study_survey.py` or `study_agent_list.py`

## Pushing to Coop

1. **Descriptive name** — used to generate the alias and description
2. **Visibility** — one of `"public"`, `"private"`, or `"unlisted"`
3. **Script** - write a short script to get the object

For 3:

```python
from study_survey import survey as obj
obj.push(
    visibility="unlisted",
    description="<paragraph description based on user's descriptive name>",
    alias="<valid-url-slug-from-descriptive-name>"
)
```
After pushing, print the results so the user can see them (URL, alias, visibility).

## Alias Rules

- Must be a valid URL slug (lowercase, hyphens, no spaces or special characters)
- Generate from the descriptive name the user provides
- Example: "US Senators 2024" -> `us-senators-2024`

## Error Handling

If the push fails (e.g., alias already taken), update the alias or description and retry.

## Quick Reference

| Task | Method |
|------|--------|
| Save locally | `obj.save('filename')` |
| Push to Coop | `obj.push(visibility=..., description=..., alias=...)` |
| Visibility options | `"public"`, `"private"`, `"unlisted"` |
