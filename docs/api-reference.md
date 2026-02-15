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
Batch processes an entire folder. Returns technical quality reports for the batch.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path to the directory. |
| `metrics` | `list[str]` | `None` | Same as `analyze_photo`. |
| `enable_subject_detection` | `bool` | `true` | Same as `analyze_photo`. |
| `model_size` | `str` | `"nano"` | `"nano"` or `"xlarge"`. |
| `limit` | `int` | `10` | Max images to process per call. |
| `offset` | `int` | `0` | Starting index for pagination. |

---

## `photographi_rank_photographs`
Burst Intelligence: Ranks photos by technical quality. Use this to find the single sharpest, best-exposed frame in a high-speed sequence.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path to the directory. |
| `top_n` | `int` | `1` | The number of top-rated images to return. |
| `limit` | `int` | `50` | Max images to process to avoid timeout. |
| `offset` | `int` | `0` | Pagination offset. |
| `metrics` | `list[str]` | `None` | Optional metric subset. |
| `enable_subject_detection` | `bool` | `true` | If true, prioritizes sharp eyes/faces. |
| `model_size` | `str` | `"nano"` | `"nano"` or `"xlarge"`. |

---

## `photographi_threshold_cull`
Binary culling: sorts into `selects/` (>= threshold) and `rejects/` (< threshold).

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path to the directory. |
| `min_confidence` | `float` | `0.6` | Images >= this score go to `selects/`. Others to `rejects/`. |
| `mode` | `str` | `"move"` | `"move"`, `"xmp"`, or `"both"`. |
| `enable_subject_detection` | `bool` | `true` | Enables subject-aware thresholding. |

---

## `photographi_cull_photographs`
Filters low-quality images into a `culled_photos/` subfolder.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path to the directory. |
| `threshold` | `float` | `0.4` | Scores below this are considered "junk". |
| `mode` | `str` | `"move"` | `"move"`, `"xmp"`, or `"both"`. |
| `enable_subject_detection` | `bool" | `true` | Enables subject-aware culling. |

---

## `photographi_get_folder_palettes`
Analyzes an entire folder and returns individual color palettes. Supports pagination.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path. |
| `colors` | `int` | `5` | Number of colors per palette. |
| `limit` | `int` | `20` | Max images per call. |
| `offset` | `int` | `0` | Starting index for pagination. |

---

## `photographi_get_scene_content`
Quick scene intelligence without full technical analysis.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image_path` | `str` | *Required* | Absolute path to RAW, JPEG, or TIFF. |

---

## `photographi_get_color_palette`
Extracts a K-Means color story (Hex codes) for style analysis.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image_path` | `str` | *Required* | Absolute path. |
| `colors` | `int` | `5` | Number of hex values to return. |
