# photographi: MCP Server
# Part of the photographi visual intelligence engine.
# License: MIT
import os
import shutil
import argparse
import time

__version__ = "0.1.0"
import logging
import gc
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
from analytics import analytics

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("photographi-mcp")

# Initialize MCP server
mcp = FastMCP("photographi")

def _analyze_photo_logic(image_path: str, metrics: list[str] = None, enable_subject_detection: bool = True, model_size: str = "nano") -> dict:
    """
    Core engine bridge for single image assessment.
    """
    if not os.path.exists(image_path):
        analytics.track_error()
        return {"error": f"File not found: {image_path}"}
        
    # Resolve relocated model path
    model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "models")
    model_filename = "yolo11n.pt" if model_size == "nano" else "yolo12x.pt"
    full_model_path = os.path.join(model_dir, model_filename)
    
    # Check if we have a local model, otherwise fallback to name-only for potential download
    if os.path.exists(full_model_path):
        model_size_or_path = full_model_path
    else:
        model_size_or_path = model_size

    # Track tool invocation already handled in wrapper, 
    # but we track specific technical details here
    format_ext = os.path.splitext(image_path)[1]
    
    start_time = time.time()
    try:
        # We don't have a direct way to measure "load time" separately here 
        # because evaluate_photo_quality handles it internally, but we can 
        # measure the total processing hit.
        res = evaluate_photo_quality(image_path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size_or_path)
        end_time = time.time()
        
        # Track Performance
        analytics.track_performance((end_time - start_time) * 1000)
        
        # Track Extensive Results
        cam_info = res.get("cameraInfo", {})
        analytics.track_analysis_results(
            judgement=res.get("judgement", "Unknown"), 
            format_ext=format_ext, 
            model_size=model_size,
            technical_score=res.get("technicalScore", 0),
            aesthetic_score=res.get("aestheticScore", 0),
            overall_score=res.get("overallConfidence", 0),
            camera_make=cam_info.get("make"),
            camera_model=cam_info.get("model"),
            lens_model=cam_info.get("lens")
        )
        if enable_subject_detection:
            analytics.track_feature_usage("subject_detection")
            
        # Trigger remote transmission attempt
        analytics.transmit_telemetry()
        return res
    except Exception as e:
        error_name = type(e).__name__
        analytics.track_error(error_name)
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
        format_ext = os.path.splitext(image_path)[1]
        start_time = time.time()
        try:
            result = evaluate_photo_quality(image_path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)
            end_time = time.time()
            
            total_confidence += result["overallConfidence"]
            
            # Performance & Extensive Tracking
            cam_info = result.get("cameraInfo", {})
            analytics.track_performance((end_time - start_time) * 1000)
            analytics.track_analysis_results(
                judgement=result.get("judgement", "Unknown"),
                format_ext=format_ext,
                model_size=model_size,
                technical_score=result.get("technicalScore", 0),
                aesthetic_score=result.get("aestheticScore", 0),
                overall_score=result.get("overallConfidence", 0),
                camera_make=cam_info.get("make"),
                camera_model=cam_info.get("model"),
                lens_model=cam_info.get("lens")
            )
            if enable_subject_detection:
                analytics.track_feature_usage("subject_detection")
            
            # Only add to detailed results if within limit
            if i < max_return:
                results[filename] = {
                    "judgement": result["judgement"],
                    "score": round(result["overallConfidence"], 3),
                    "summary": result.get("reasoning", {}).get("technical", "Good.")
                }
        except Exception as e:
            analytics.track_error()
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
    
    # Trigger remote transmission attempt
    analytics.transmit_telemetry()
    
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
        format_ext = os.path.splitext(path)[1]
        start_time = time.time()
        try:
            res = evaluate_photo_quality(path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)
            end_time = time.time()
            
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
            
            # Performance & Extensive Tracking
            cam_info = res.get("cameraInfo", {})
            analytics.track_performance((end_time - start_time) * 1000)
            analytics.track_analysis_results(
                judgement=res.get("judgement", "Unknown"),
                format_ext=format_ext,
                model_size=model_size,
                technical_score=res.get("technicalScore", 0),
                aesthetic_score=res.get("aestheticScore", 0),
                overall_score=res.get("overallConfidence", 0),
                camera_make=cam_info.get("make"),
                camera_model=cam_info.get("model"),
                lens_model=cam_info.get("lens")
            )
            if enable_subject_detection:
                analytics.track_feature_usage("subject_detection")

        except Exception as e:
            analytics.track_error(type(e).__name__)
            logger.error(f"Failed to rank {filename}: {e}")
            continue
        gc.collect()
            
    scored_images.sort(key=lambda x: x["score"], reverse=True)
    # Trigger remote transmission attempt after batch
    analytics.transmit_telemetry()
    return {
        "status": "Ranking Complete", 
        "totalImagesScanned": len(image_files), 
        "bestImages": scored_images[:top_n]
    }

def _threshold_cull_logic(folder_path: str, min_confidence: float = 0.6, mode: str = "move", metrics: list[str] = None, enable_subject_detection: bool = True, model_size: str = "nano") -> dict:
    """
    Binary culling based on strict confidence threshold.
    
    Workflow:
    Unlike qualitative culling (Good/Fair/Poor), this uses a deterministic
    numerical threshold. Images >= min_confidence go to 'selects/', 
    others to 'rejects/'.
    
    Ideal for: High-volume shoots where you want binary decisions
    (e.g., "Keep anything above 0.7").
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"error": "Directory not found."}
        
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS) and not f.startswith(".")]
    if not image_files:
        return {"message": "No images found."}
        
    selects_dir = os.path.join(folder_path, "selects")
    rejects_dir = os.path.join(folder_path, "rejects")
    
    if mode in ["move", "both"]:
        os.makedirs(selects_dir, exist_ok=True)
        os.makedirs(rejects_dir, exist_ok=True)
    
    selects = []
    rejects = []
    
    for filename in tqdm(image_files, desc="Threshold culling"):
        path = os.path.join(folder_path, filename)
        format_ext = os.path.splitext(path)[1]
        start_time = time.time()
        try:
            res = evaluate_photo_quality(path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)
            end_time = time.time()
            confidence = res["overallConfidence"]
            
            # Performance & Extensive Tracking
            cam_info = res.get("cameraInfo", {})
            analytics.track_performance((end_time - start_time) * 1000)
            analytics.track_analysis_results(
                judgement=res.get("judgement", "Unknown"),
                format_ext=format_ext,
                model_size=model_size,
                technical_score=res.get("technicalScore", 0),
                aesthetic_score=res.get("aestheticScore", 0),
                overall_score=res.get("overallConfidence", 0),
                camera_make=cam_info.get("make"),
                camera_model=cam_info.get("model"),
                lens_model=cam_info.get("lens")
            )
            if enable_subject_detection:
                analytics.track_feature_usage("subject_detection")

            target_list = selects if confidence >= min_confidence else rejects
            target_dir = selects_dir if confidence >= min_confidence else rejects_dir
            
            actions = []
            if mode in ["xmp", "both"]:
                status = "Keep" if confidence >= min_confidence else "Rejected"
                create_xmp_sidecar(path, status, confidence)
                actions.append("XMP-Tagged")
                analytics.track_feature_usage("xmp_sidecar")
                
            if mode in ["move", "both"]:
                try:
                    dest = os.path.join(target_dir, filename)
                    shutil.move(path, dest)
                    xmp_path = os.path.splitext(path)[0] + ".xmp"
                    if os.path.exists(xmp_path):
                        shutil.move(xmp_path, os.path.join(target_dir, os.path.basename(xmp_path)))
                    actions.append("Moved")
                except Exception as e:
                    logger.error(f"Failed to move {filename}: {e}")
                    actions.append("Move-Failed")
                    
            target_list.append({"filename": filename, "score": round(confidence, 3), "actions": actions})
            
        except Exception as e:
            logger.error(f"Failed to analyze {filename}: {e}")
            continue
        gc.collect()
    
    return {
        "status": "Threshold Culling Complete",
        "threshold": min_confidence,
        "totalImagesScanned": len(image_files),
        "selectsCount": len(selects),
        "rejectsCount": len(rejects),
        "selects": selects[:10],  # Sample
        "rejects": rejects[:10]   # Sample
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
        format_ext = os.path.splitext(path)[1]
        start_time = time.time()
        try:
            res = evaluate_photo_quality(path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)
            end_time = time.time()
            
            scored_images.append({"filename": filename, "path": path, "score": res["overallConfidence"], "judgement": res.get("judgement", "Unknown")})
            
            # Performance & Extensive Tracking
            cam_info = res.get("cameraInfo", {})
            analytics.track_performance((end_time - start_time) * 1000)
            analytics.track_analysis_results(
                judgement=res.get("judgement", "Unknown"),
                format_ext=format_ext,
                model_size=model_size,
                technical_score=res.get("technicalScore", 0),
                aesthetic_score=res.get("aestheticScore", 0),
                overall_score=res.get("overallConfidence", 0),
                camera_make=cam_info.get("make"),
                camera_model=cam_info.get("model"),
                lens_model=cam_info.get("lens")
            )
            if enable_subject_detection:
                analytics.track_feature_usage("subject_detection")

        except Exception as e:
            analytics.track_error(type(e).__name__)
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
                analytics.track_feature_usage("xmp_sidecar")
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
    image_path: Annotated[str, Field(description="Absolute path to RAW/JPEG/TIFF.")],
    metrics: Annotated[list[str], Field(description="Optional: specific metrics (sharpness, exposure, noise, focus, color, dynamicRange, composition). Defaults to all.")] = None,
    enable_subject_detection: Annotated[bool, Field(description="Enables YOLOv11 for Subject-Aware Metering and ROI focus analysis.")] = True,
    model_size: Annotated[Literal["nano", "xlarge"], Field(description="YOLO model size. 'nano' is sub-second; 'xlarge' is studio-grade.")] = "nano"
) -> dict:
    """
    Performs Studio-Grade technical analysis on a single photo.
    
    Science:
    - Exposure: Evaluated via the Ansel Adams Zone System.
    - Sharpness: Lens-aware calculation with Diffraction Limited Aperture (DLA) detection.
    - AI Context: Uses Subject-Aware Metering to prioritize detected faces/objects.
    """
    analytics.track_tool_invocation("photographi_analyze_photo")
    return _analyze_photo_logic(image_path, metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)

@mcp.tool()
def photographi_analyze_folder(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    metrics: Annotated[list[str], Field(description="Metrics to calculate.")] = None,
    enable_subject_detection: bool = True,
    model_size: Annotated[Literal["nano", "xlarge"], Field(description="YOLO model size.")] = "nano"
) -> dict:
    """
    Batch analyzes an entire folder. 
    Returns a technical sample of results. Use for quick library auditing.
    """
    analytics.track_tool_invocation("photographi_analyze_folder")
    return _analyze_folder_logic(folder_path, metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)

@mcp.tool()
def photographi_rank_photographs(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    top_n: Annotated[int, Field(description="Number of top-rated images to return.")] = 1,
    metrics: list[str] = None,
    enable_subject_detection: bool = True,
    model_size: Annotated[Literal["nano", "xlarge"], Field(description="YOLO model size.")] = "nano"
) -> dict:
    """
    Burst Intelligence: Ranks photos by technical quality. 
    Use this to find the single sharpest, best-exposed frame in a high-speed sequence.
    """
    analytics.track_tool_invocation("photographi_rank_photographs")
    return _rank_folder_logic(folder_path, top_n=top_n, metrics=metrics, enable_subject_detection=enable_subject_detection, model_size=model_size)

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
def photographi_threshold_cull(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    min_confidence: Annotated[float, Field(
        description="Minimum confidence threshold (0.0-1.0). Images below this are rejected.",
        ge=0.0,
        le=1.0
    )] = 0.6,
    mode: Annotated[Literal["move", "xmp", "both"], Field(description="Cull mode.")] = "move",
    enable_subject_detection: bool = True
) -> dict:
    """Binary culling: sorts into 'selects/' (>= threshold) and 'rejects/' (< threshold)."""
    return _threshold_cull_logic(folder_path, min_confidence, mode, enable_subject_detection=enable_subject_detection)

@mcp.tool()
def photographi_get_color_palette(
    image_path: Annotated[str, Field(description="Absolute path to image.")],
    colors: int = 5
) -> dict:
    """
    Extracts a representative color palette using K-Means Clustering.
    """
    analytics.track_tool_invocation("photographi_get_color_palette")
    palette = generate_color_palette(image_path, colors)
    analytics.track_feature_usage("color_palette")
    return {"colors": palette}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Photographi MCP Server")
    parser.add_argument("--telemetry-endpoint", help="Remote telemetry collection URL")
    parser.add_argument("--disable-telemetry", action="store_true", help="Disable all local and remote analytics")
    args, unknown = parser.parse_known_args()
    
    # Configure analytics from CLI args
    analytics.configure(
        endpoint=args.telemetry_endpoint,
        disabled=True if args.disable_telemetry else None
    )
    
    mcp.run()
