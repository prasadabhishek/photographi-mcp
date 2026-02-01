import gc
import json
import logging
import os
import shutil
from typing import Annotated, Literal

from pydantic import Field
from fastmcp import FastMCP
from tqdm import tqdm

from photo_quality_analyzer_core.analyzer import (
    evaluate_photo_quality,
    SUPPORTED_EXTENSIONS,
    create_xmp_sidecar,
    generate_color_palette,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("photographi-mcp")

# Initialize MCP server
mcp = FastMCP("photographi")

def _analyze_photo_logic(image_path: str, metrics: list[str] = None, enable_subject_detection: bool = True, model_size: str = "nano") -> dict:
    """
    Core engine bridge for single image assessment.
    
    This function acts as the primary adapter between the MCP tool interface 
    and the core signal processing library. It handles absolute path validation 
    and delegates heavy lifting to the `evaluate_photo_quality` pipeline.
    
    Ref: [analyzer.py:evaluate_photo_quality](file:///Users/abhishekprasad/workspace/photo-quality-analyzer/photo_quality_analyzer_core/analyzer.py)
    """
    if not os.path.exists(image_path):
        return {"error": f"File not found: {image_path}"}
    try:
        return evaluate_photo_quality(image_path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)
    except Exception as e:
        logger.error(f"Error analyzing {image_path}: {e}")
        return {"error": str(e)}

def _analyze_folder_logic(folder_path: str, metrics: list[str] = None, enable_subject_detection: bool = True, model_size: str = "nano") -> list[dict]:
    """
    Batch processing pipeline for directory-scale analysis.
    
    Implements a recursive search for all supported image formats. To maintain
    responsive MCP communication, results are capped at 50, but full culling
    functionality is available via the `cull_folder` tool.
    
    Design:
    Uses `tqdm` for terminal progress tracking while running analysis in 
    a single-threaded loop to prioritize local memory stability over raw speed.
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"error": f"Directory not found: {folder_path}"}
    
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS) and not f.startswith(".")]
    if not image_files:
        return {"message": "No images found in the folder."}
    
    results = {}
    total_confidence = 0
    # Process all but limit the returned JSON size to prevent 400 Invalid Request Body
    max_return = 10 
    
    for i, filename in enumerate(tqdm(image_files, desc="Analyzing folder")):
        image_path = os.path.join(folder_path, filename)
        try:
            result = evaluate_photo_quality(image_path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)
            total_confidence += result["overallConfidence"]
            
            # Only add to detailed results if within limit
            if i < max_return:
                results[filename] = {
                    "judgement": result["judgement"],
                    "score": round(result["overallConfidence"], 3),
                    "summary": result.get("reasoning", {}).get("technical", "Good.")
                }
        except Exception as e:
            if i < max_return:
                results[filename] = {"error": str(e)}
        gc.collect()
            
    avg_conf = round(total_confidence / len(image_files), 3) if image_files else 0
    
    response = {
        "status": "Analysis Complete",
        "totalImagesScanned": len(image_files),
        "averageConfidence": avg_conf,
        "sampleResults": results
    }
    
    if len(image_files) > max_return:
        response["note"] = f"Showing first {max_return} of {len(image_files)} images. Request a ranking or specific file analysis for more."
        
    return response

def _rank_folder_logic(folder_path: str, top_n: int = 10, metrics: list[str] = None, enable_subject_detection: bool = True, model_size: str = "nano") -> list[dict]:
    """
    Burst-selection Intelligence: Finding the sharpest needle in the haystack.
    
    Science:
    Sorts files by the `overallConfidence` score, which is a weighted sum 
    of technical execution (Exposure, Sharpness, Noise) and aesthetic 
    composition.
    
    Workflow:
    Ideal for photographers who shoot in 'Burst Mode' and need the single 
    best-executed frame from a high-speed sequence.
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"error": f"Directory not found: {folder_path}"}
    
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS) and not f.startswith(".")]
    if not image_files:
        return {"message": "No images found."}
        
    scored_images = []
    for filename in image_files:
        path = os.path.join(folder_path, filename)
        try:
            res = evaluate_photo_quality(path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)
            scored_images.append({
                "filename": filename,
                "score": round(res["overallConfidence"], 3),
                "judgement": res["judgement"],
                "summary": res.get("judgementDescription", ""),
                "technicalScore": round(res.get("technicalScore", 0), 2),
                "aestheticScore": round(res.get("aestheticScore", 0), 2),
                "metrics": {
                    "sharpness": round(res.get("metrics", {}).get("sharpness", {}).get("score", 0), 2),
                    "exposure": round(res.get("metrics", {}).get("exposure", {}).get("score", 0), 2),
                    "noise": round(res.get("metrics", {}).get("noise", {}).get("score", 0), 2),
                    "color": round(res.get("metrics", {}).get("color", {}).get("score", 0), 2),
                    "dynamicRange": round(res.get("metrics", {}).get("dynamicRange", {}).get("score", 0), 2),
                    "focus": round(res.get("metrics", {}).get("focus", {}).get("score", 0), 2) if "focus" in res.get("metrics", {}) else None
                }
            })
        except: continue
        gc.collect()
            
    scored_images.sort(key=lambda x: x["score"], reverse=True)
    return {
        "status": "Ranking Complete", 
        "totalImagesScanned": len(image_files), 
        "bestImages": scored_images[:top_n]
    }

def _cull_folder_logic(folder_path: str, threshold: float = 0.4, keep_best_n: int = None, mode: str = "move", metrics: list[str] = None, enable_subject_detection: bool = True, model_size: str = "nano") -> dict:
    """
    Automated Content Culling and Asset Management.
    
    Decision Logic:
    1. Every photo is evaluated using the full technical + aesthetic pipeline.
    2. Any photo with an `overallConfidence` below the `threshold` is flagged.
    
    Action Modes:
    - `move`: Physically relocates rejected shots to a `culled_photos` folder.
    - `xmp`: Generates XMP sidecars with "Rejected" labels (Safe path).
    - `both`: Performs relocation and metadata tagging.
    
    Science of 'Keep Best N':
    Ensures that even in a low-quality burst, the top N frames are preserved, 
    preventing over-aggressive data loss.
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"error": "Directory not found."}
        
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    if not image_files:
        return {"message": "No images found."}
        
    scored_images = []
    for filename in tqdm(image_files, desc="Visual intelligence analysis"):
        path = os.path.join(folder_path, filename)
        try:
            res = evaluate_photo_quality(path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)
            scored_images.append({"filename": filename, "path": path, "score": res["overallConfidence"]})
        except Exception as e:
            logger.error(f"Failed to analyze {filename}: {e}")
            continue
        gc.collect()
            
    rejects = []
    if keep_best_n is not None:
        scored_images.sort(key=lambda x: x["score"], reverse=True)
        rejects = scored_images[keep_best_n:]
    else:
        rejects = [img for img in scored_images if img["score"] < threshold]
        
    culled_results = []
    if rejects:
        culled_dir = os.path.join(folder_path, "culled_photos")
        if mode in ["move", "both"] and not os.path.exists(culled_dir):
            os.makedirs(culled_dir)
            
        for img in rejects:
            status_actions = []
            if mode in ["xmp", "both"]:
                create_xmp_sidecar(img["path"], "Rejected", img["score"])
                status_actions.append("XMP-Tagged")
            if mode in ["move", "both"]:
                try:
                    dest = os.path.join(culled_dir, img["filename"])
                    shutil.move(img["path"], dest)
                    xmp_path = os.path.splitext(img["path"])[0] + ".xmp"
                    if os.path.exists(xmp_path):
                        shutil.move(xmp_path, os.path.join(culled_dir, os.path.basename(xmp_path)))
                    status_actions.append("Moved")
                except Exception as e:
                    logger.error(f"Failed to move {img['filename']}: {e}")
                    status_actions.append("Move-Failed")
            culled_results.append({"filename": img["filename"], "score": round(img["score"], 2), "actions": status_actions})
            
    summary_msg = f"SUCCESS: Analyzed {len(image_files)} photos. Culled {len(culled_results)} images into '{mode}' state."
    return {
        "status": "Action Complete",
        "message": summary_msg,
        "totalImagesScanned": len(image_files),
        "culledCount": len(culled_results)
    }

@mcp.tool()
def photographi_analyze_photo(
    image_path: Annotated[str, Field(description="Absolute path to RAW/JPEG.")],
    metrics: Annotated[list[str], Field(description="Metrics (e.g. ['sharpness']).")] = None,
    enable_subject_detection: bool = True,
    model_size: str = "nano"
) -> dict:
    """Performs technical quality analysis on a single photo."""
    return _analyze_photo_logic(image_path, metrics, enable_subject_detection, model_size)

@mcp.tool()
def photographi_analyze_folder(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    metrics: list[str] = None,
    enable_subject_detection: bool = True,
    model_size: str = "nano"
) -> dict:
    """Batch analyzes an entire folder. Returns sample results."""
    return _analyze_folder_logic(folder_path, metrics, enable_subject_detection, model_size)

@mcp.tool()
def photographi_rank_photographs(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    top_n: int = 1,
    metrics: list[str] = None,
    enable_subject_detection: bool = True,
    model_size: str = "nano"
) -> dict:
    """Ranks photos by technical quality. Use for finding the best shot in a burst."""
    return _rank_folder_logic(folder_path, top_n, metrics, enable_subject_detection, model_size)

@mcp.tool()
def photographi_cull_photographs(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    threshold: float = 0.4,
    mode: Annotated[Literal["move", "xmp", "both"], Field(description="Cull mode.")] = "move",
    enable_subject_detection: bool = True
) -> dict:
    """Filters low-quality images into a 'culled_photos' subfolder."""
    return _cull_folder_logic(folder_path, threshold, mode=mode, enable_subject_detection=enable_subject_detection)

@mcp.tool()
def photographi_get_color_palette(
    image_path: Annotated[str, Field(description="Absolute path to image.")],
    colors: int = 5
) -> dict:
    """
    Extracts a representative color palette from an image.
    
    Science:
    Uses K-Means clustering in RGB space to identify dominant color clusters.
    Returns: {"colors": ["#hex1", "#hex2", ...]}
    """
    if not os.path.exists(image_path): return {"error": "File not found."}
    palette = generate_color_palette(image_path, colors)
    return {"colors": palette}

if __name__ == "__main__":
    mcp.run()
