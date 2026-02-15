# Axiom Field Limit Mitigation Plan

Axiom's 256-field limit is triggered when unique strings (camera names, lens models) are used as JSON keys, because each key becomes a column. We will refactor the transmission logic to use a "Column-Stable" format.

## Proposed Changes

### [photographi]

#### [MODIFY] [analytics.py](file:///Users/abhishekprasad/workspace/photographi/analytics.py)
Update `transmit_telemetry` to transform the local snapshot into a list of "Batch Events".

- **Event 1 (Global)**: Contains summary stats (total images, average processing time, environment).
- **Events 2-N (Distributions)**: Each unique camera, lens, format, or tool will be sent as a separate object in the list with `label` and `value` fields.

**New Schema and APL Mapping:**
```json
[
  {"event_type": "global_state", "total_images": 100, ...},
  {"event_type": "distribution", "category": "camera", "label": "Sony A7IV", "value": 10},
  {"event_type": "distribution", "category": "lens", "label": "24-70mm", "value": 5}
]
```

## Verification Plan

### Automated Tests
- Run `populate_axiom.py` and verify it transmits an array of objects.
- Inspect the output in the terminal to ensure transformation logic is correct.

### Manual Verification
- Verify in Axiom that the field count remains stable (only ~10-15 fields discovered total).
