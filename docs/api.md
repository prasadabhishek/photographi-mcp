# 🛠️ MCP Tool Reference

This document provides a detailed breakdown of every tool exposed by the **photographi** MCP server.

---

## `analyze_photo`
Analyzes a single image file for technical and aesthetic quality.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image_path` | `str` | *Required* | Absolute path to the image or RAW file. |
| `metrics` | `list[str]` | `None` | Optional subset of metrics: `sharpness`, `focus`, `exposure`, `noise`, `color`, `dynamicRange`, `composition`. |
| `enable_subject_detection` | `bool` | `true` | If `false`, YOLO detection is skipped for high speed. |

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

## `analyze_folder`
Bulk analysis of all supported images in a directory.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path to the directory. |
| `metrics` | `list[str]` | `None` | Same as `analyze_photo`. |
| `enable_subject_detection` | `bool` | `true` | Same as `analyze_photo`. |

---

## `rank_folder`
Finds the cream of the crop in a directory.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path to the directory. |
| `top_n` | `int` | `10` | The number of top-scored images to return. |

---

## `cull_folder`
The master cleanup tool for professional photographers.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `folder_path` | `str` | *Required* | Absolute path. |
| `threshold` | `float` | `0.4` | Scores below this are rejected. |
| `keep_best_n` | `int` | `None` | If set, overrides `threshold` to keep exactly the Top N. |
| `mode` | `str` | `"xmp"` | `"xmp"`, `"move"`, or `"both"`. |

---

## `get_color_palette`
Extracts dominant colors from an image.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `image_path` | `str` | *Required* | Absolute path. |
| `colors` | `int` | `5` | Number of hex values to return. |
