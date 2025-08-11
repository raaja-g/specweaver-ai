### Schemas (concise)

#### Requirement Graph (JSON shape)

```json
{
  "$id": "RequirementGraph",
  "type": "object",
  "required": [
    "id",
    "title",
    "actor",
    "goal",
    "benefit",
    "acceptanceCriteria",
    "domainEntities",
    "assumptions",
    "risks",
    "tags"
  ],
  "properties": {
    "id": { "type": "string" },
    "title": { "type": "string" },
    "actor": { "type": "string" },
    "goal": { "type": "string" },
    "benefit": { "type": "string" },
    "preconditions": { "type": "array", "items": { "type": "string" } },
    "acceptanceCriteria": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "given", "when", "then"],
        "properties": {
          "id": { "type": "string" },
          "given": { "type": "string" },
          "when": { "type": "string" },
          "then": { "type": "string" },
          "notes": { "type": "string" }
        }
      }
    },
    "constraints": { "type": "array", "items": { "type": "string" } },
    "domainEntities": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name"],
        "properties": {
          "name": { "type": "string" },
          "fields": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "assumptions": { "type": "array", "items": { "type": "string" } },
    "risks": { "type": "array", "items": { "type": "string" } },
    "tags": { "type": "array", "items": { "type": "string" } }
  }
}
```

#### Test Case (JSON shape)

```json
{
  "$id": "TestCase",
  "type": "object",
  "required": [
    "id",
    "title",
    "priority",
    "traceTo",
    "preconditions",
    "steps",
    "data",
    "expected",
    "type",
    "tags"
  ],
  "properties": {
    "id": { "type": "string" },
    "title": { "type": "string" },
    "priority": { "type": "string", "enum": ["P0", "P1", "P2"] },
    "type": { "type": "string", "enum": ["positive", "negative", "edge"] },
    "traceTo": { "type": "array", "items": { "type": "string" } },
    "preconditions": { "type": "array", "items": { "type": "string" } },
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["action", "params"],
        "properties": {
          "action": { "type": "string" },
          "params": { "type": "object", "additionalProperties": true }
        }
      }
    },
    "data": { "type": "object", "additionalProperties": true },
    "expected": { "type": "array", "items": { "type": "string" } },
    "tags": { "type": "array", "items": { "type": "string" } }
  }
}
```

