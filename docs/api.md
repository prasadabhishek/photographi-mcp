# 🛠️ MCP Tool Reference

This document provides a detailed breakdown of every tool exposed by the **photographi** MCP server.

---

## `photographi_analyze_photo`
Performs Studio-Grade technical analysis on a single photo.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image_path` | `str` | *Required* | Absolute path to RAW, JPEG, or TIFF. |
| `metrics` | `list[str]` | `None` | Optional subset: `sharpness`, `exposure`, `noise`, `focus`, `color`, `dynamicRange`, `composition`. |
| `enable_subject_detection` | `bool` | `true` | Enables YOLO for Subject-Aware Metering. |
| `model_size` | `str` | `"nano"` | `"nano"` (fast, <1s) or `"xlarge"` (ultra-precise). |

**Example Response**:
```json
{
  "sharpness": 0.85,
  "exposure": 0.92,
  "judgement": "Good",
  "overallConfidence": 0.78
}
```

---

## `photographi_analyze_folder`
Batch processes an entire folder. Returns a statistical sample (capped at 50 for performance).

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path to the directory. |
| `metrics` | `list[str]` | `None` | Same as `analyze_photo`. |
| `enable_subject_detection` | `bool` | `true` | Same as `analyze_photo`. |
| `model_size` | `str` | `"nano"` | `"nano"` or `"xlarge"`. |

---

## `photographi_rank_photographs`
Ranks a group of photos by `overallConfidence`. Ideal for finding the "keeper" in a burst sequence.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path to the directory. |
| `top_n` | `int` | `10` | The number of top-scored images to return. |
| `metrics` | `list[str]` | `None` | Optional metric subset. |
| `enable_subject_detection` | `bool` | `true` | If true, prioritizes sharp eyes/faces. |
| `model_size` | `str` | `"nano"` | `"nano"` or `"xlarge"`. |

---

## `photographi_threshold_cull`
Binary culling: Sorts images based on a strict numerical quality threshold.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path to the directory. |
| `min_confidence` | `float` | `0.6` | Images >= this score go to `selects/`. Others to `rejects/`. |
| `mode` | `str` | `"move"` | `"move"` (physically move files), `"xmp"` (tag metadata), or `"both"`. |
| `enable_subject_detection` | `bool` | `true` | If true, prioritized sharp eyes/faces. |

---

## `photographi_cull_photographs`
Qualitative culling: Filters low-quality assets into a `culled_photos/` subfolder.

### `photographi_get_folder_palettes`
Analyzes an entire folder and returns individual color palettes. Supports pagination.

**Parameters:**
- `folder_path` (string, required): Absolute path to the directory.
- `colors` (integer, optional): Number of colors per palette. Default: 5.
- `limit` (integer, optional): Max images to process per call. Default: 20.
- `offset` (integer, optional): Starting index for pagination. Default: 0.

**Example Prompt:**
> "Extract 5-color palettes for the first 50 images in the 'vacation' folder."

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path. |
| `threshold` | `float` | `0.4` | Scores below this are considered "junk". |
| `mode` | `str` | `"move"` | `"move"`, `"xmp"`, or `"both"`. |
| `enable_subject_detection` | `bool` | `true` | If true, prioritized sharp eyes/faces. |

---

## `photographi_get_color_palette`
Extracts a K-Means color story (Hex codes) for style analysis.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image_path` | `str` | *Required* | Absolute path. |
| `colors` | `int` | `5` | Number of hex values to return. |
