# photographi: MCP Server
# Part of the photographi visual intelligence engine.
# License: MIT
import os
import shutil
import argparse
import time
import logging
import sys
import gc
import concurrent.futures
from typing import Annotated, Literal

from pydantic import Field
from fastmcp import FastMCP
from photo_quality_analyzer_core.analyzer import (
    evaluate_photo_quality,
    detect_objects,
    SUPPORTED_EXTENSIONS,
    create_xmp_sidecar,
    generate_color_palette,
)
from analytics import analytics

# Setup logging - Force to stderr to avoid breaking MCP protocol
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("photographi-mcp")

# Initialize MCP server
mcp = FastMCP("photographi")

def _validate_path(path: str, must_exist: bool = True, expected_type: Literal["file", "dir", "any"] = "any") -> str:
    """
    Validates a file path for security and existence.
    """
    if not path:
        raise ValueError("Path cannot be empty")
        
    abs_path = os.path.abspath(os.path.expanduser(path))
    
    if must_exist and not os.path.exists(abs_path):
        raise ValueError(f"Path not found: {path}")
        
    if must_exist:
        if expected_type == "file" and not os.path.isfile(abs_path):
            raise ValueError(f"Expected file but found directory: {path}")
        if expected_type == "dir" and not os.path.isdir(abs_path):
            raise ValueError(f"Expected directory but found file: {path}")
            
    return abs_path

def _process_single_image(
    filename: str,
    folder_path: str,
    metrics: list[str] = None,
    enable_subject_detection: bool = True,
    model_size: str = "nano",
    fast_mode: bool = False
) -> dict:
    """
    General purpose worker for concurrent image analysis.
    """
    path = os.path.join(folder_path, filename)
    format_ext = os.path.splitext(path)[1]
    start_time = time.time()
    try:
        # Resolve relocated model path if necessary
        model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "models")
        model_filename = "yolo26n.onnx" if model_size == "nano" else "yolo11x.onnx"
        full_model_path = os.path.join(model_dir, model_filename)
        model_ptr = full_model_path if os.path.exists(full_model_path) else model_size

        res = evaluate_photo_quality(
            path, 
            requested_metrics=metrics, 
            enable_subject_detection=enable_subject_detection, 
            model_size=model_ptr,
            force_downsample=fast_mode
        )
        end_time = time.time()
        
        # Telemetry
        analytics.track_performance((end_time - start_time) * 1000)
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
            
        # Return full result but allow caller to filter
        res["filename"] = filename
        res["path"] = path
        return res
    except Exception as e:
        logger.error(f"Failed to analyze {filename}: {e}")
        return {"filename": filename, "error": str(e), "overallConfidence": 0}
    finally:
        gc.collect()

def _analyze_photo_logic(image_path: str, metrics: list[str] = None, enable_subject_detection: bool = True, model_size: str = "nano", fast_mode: bool = False) -> dict:
    """Single image assessment bridge."""
    try:
        image_path = _validate_path(image_path, expected_type="file")
    except ValueError as e:
        return {"error": str(e)}
    
    # Use the helper even for single images to keep logic centralized
    return _process_single_image(os.path.basename(image_path), os.path.dirname(image_path), metrics, enable_subject_detection, model_size, fast_mode)

def _batch_executor(
    folder_path: str,
    paginated_files: list[str],
    metrics: list[str],
    enable_subject_detection: bool,
    model_size: str,
    fast_mode: bool
) -> list[dict]:
    """Internal helper to run the thread pool."""
    max_workers = min(os.cpu_count() or 4, len(paginated_files))
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(
                _process_single_image,
                fname,
                folder_path,
                metrics,
                enable_subject_detection,
                model_size,
                fast_mode
            ): fname for fname in paginated_files
        }
        for future in concurrent.futures.as_completed(future_to_file):
            results.append(future.result())
    return results

def _analyze_folder_logic(folder_path: str, metrics: list[str] = None, enable_subject_detection: bool = True, model_size: str = "nano", limit: int = 10, offset: int = 0, fast_mode: bool = False) -> dict:
    """Batch analysis with concurrency and pagination."""
    try:
        folder_path = _validate_path(folder_path, expected_type="dir")
    except ValueError as e:
        return {"error": str(e)}
    
    image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS) and not f.startswith(".")])
    if not image_files: return {"message": "No images found."}
    
    total_images = len(image_files)
    paginated_files = image_files[offset : offset + limit]
    if not paginated_files: return {"message": "No more images in range.", "totalImages": total_images}

    raw_results = _batch_executor(folder_path, paginated_files, metrics, enable_subject_detection, model_size, fast_mode)
    
    # Filter for output cleanliness
    formatted_results = {}
    total_conf = 0
    for res in raw_results:
        if "error" in res:
            formatted_results[res["filename"]] = {"error": res["error"]}
        else:
            total_conf += res["overallConfidence"]
            formatted_results[res["filename"]] = {
                "judgement": res["judgement"],
                "score": round(res["overallConfidence"], 3),
                "summary": res.get("reasoning", {}).get("technical", "Good.")
            }
            
    response = {
        "status": "Analysis Complete",
        "totalImagesInFolder": total_images,
        "processed": len(raw_results),
        "offset": offset,
        "limit": limit,
        "averageConfidence": round(total_conf / len(raw_results), 3) if raw_results else 0,
        "results": formatted_results
    }
    if offset + limit < total_images:
        response["nextOffset"] = offset + limit
    
    analytics.transmit_telemetry()
    return response

def _rank_folder_logic(folder_path: str, top_n: int = 10, limit: int = 50, offset: int = 0, metrics: list[str] = None, enable_subject_detection: bool = True, model_size: str = "nano", fast_mode: bool = False) -> dict:
    """Concurrent ranking logic."""
    try:
        folder_path = _validate_path(folder_path, expected_type="dir")
    except ValueError as e:
        return {"error": str(e)}

    image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS) and not f.startswith(".")])
    if not image_files: return {"message": "No images found."}

    total_images = len(image_files)
    paginated_files = image_files[offset : offset + limit]
    if not paginated_files: return {"message": "No more images.", "totalImages": total_images}

    raw_results = _batch_executor(folder_path, paginated_files, metrics, enable_subject_detection, model_size, fast_mode)
    
    # Sort and format
    scored = []
    for res in raw_results:
        if "error" in res: continue
        scored.append({
            "filename": res["filename"],
            "score": round(res["overallConfidence"], 3),
            "judgement": res["judgement"],
            "summary": res.get("judgementDescription", ""),
            "technicalScore": round(res.get("technicalScore", 0), 2),
            "metrics": {k: round(v.get("score", 0), 2) for k, v in res.get("metrics", {}).items() if isinstance(v, dict)}
        })
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    
    response = {
        "status": "Ranking Complete",
        "totalImagesInFolder": total_images,
        "processed": len(scored),
        "offset": offset,
        "limit": limit,
        "bestImages": scored[:top_n]
    }
    if offset + limit < total_images:
        response["nextOffset"] = offset + limit

    analytics.transmit_telemetry()
    return response

def _cull_logic(folder_path: str, threshold: float = 0.4, mode: str = "move", is_threshold_mode: bool = False, metrics: list[str] = None, enable_subject_detection: bool = True, model_size: str = "nano", limit: int = 50, offset: int = 0, fast_mode: bool = False) -> dict:
    """Unified concurrent culling logic (Threshold vs Qualitative)."""
    try:
        folder_path = _validate_path(folder_path, expected_type="dir")
    except ValueError as e:
        return {"error": str(e)}

    image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS) and not f.startswith(".")])
    if not image_files: return {"message": "No images found."}

    total_images = len(image_files)
    paginated_files = image_files[offset : offset + limit]
    if not paginated_files: return {"message": "No more images.", "totalImages": total_images}

    # Setup directories
    target_subdir = "selects" if is_threshold_mode else "kept_photos"
    reject_subdir = "rejects" if is_threshold_mode else "culled_photos"
    target_dir = os.path.join(folder_path, target_subdir)
    reject_dir = os.path.join(folder_path, reject_subdir)
    
    if mode in ["move", "both"]:
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(reject_dir, exist_ok=True)

    raw_results = _batch_executor(folder_path, paginated_files, metrics, enable_subject_detection, model_size, fast_mode)
    
    culled_items = []
    kept_items = []
    
    for res in raw_results:
        if "error" in res: continue
        filename = res["filename"]
        path = res["path"]
        score = res["overallConfidence"]
        
        is_select = score >= threshold
        dest_dir = target_dir if is_select else reject_dir
        actions = []

        if mode in ["xmp", "both"]:
            status = "Keep" if is_select else "Rejected"
            create_xmp_sidecar(path, status, score)
            actions.append("XMP-Tagged")
            
        if mode in ["move", "both"]:
            try:
                shutil.move(path, os.path.join(dest_dir, filename))
                xmp_path = os.path.splitext(path)[0] + ".xmp"
                if os.path.exists(xmp_path):
                    shutil.move(xmp_path, os.path.join(dest_dir, os.path.basename(xmp_path)))
                actions.append("Moved")
            except Exception as e:
                logger.error(f"Move failed for {filename}: {e}")
                actions.append("Move-Failed")
        
        item = {"filename": filename, "score": round(score, 3), "actions": actions}
        if is_select: kept_items.append(item)
        else: culled_items.append(item)

    status_msg = "Threshold Culling Complete" if is_threshold_mode else "Culling Complete"
    response = {
        "status": status_msg,
        "totalImagesInFolder": total_images,
        "processed": len(raw_results),
        "keptCount": len(kept_items),
        "rejectedCount": len(culled_items),
        "offset": offset,
        "limit": limit,
        "resultsSample": (kept_items + culled_items)[:10]
    }
    if offset + limit < total_images:
        response["nextOffset"] = offset + limit
    
    analytics.transmit_telemetry()
    return response

@mcp.tool()
def photographi_analyze_photo(
    image_path: Annotated[str, Field(description="Absolute path to RAW/JPEG/TIFF.")],
    metrics: Annotated[list[str], Field(description="Specific metrics (sharpness, exposure, noise, focus, color, dynamicRange, composition).")] = None,
    enable_subject_detection: bool = True,
    model_size: Annotated[Literal["nano", "xlarge"], Field(description="YOLO model size.")] = "nano",
    fast_mode: Annotated[bool, Field(description="Set to True for faster analysis by downsampling high-res images.")] = False
) -> dict:
    """Performs Studio-Grade technical analysis on a single photo."""
    analytics.track_tool_invocation("photographi_analyze_photo")
    return _analyze_photo_logic(image_path, metrics, enable_subject_detection, model_size, fast_mode)

@mcp.tool()
def photographi_analyze_folder(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    metrics: Annotated[list[str], Field(description="Specific metrics to calculate (sharpness, exposure, etc.). Defaults to all.")] = None,
    enable_subject_detection: Annotated[bool, Field(description="Use AI for subject-aware analysis.")] = True,
    model_size: Annotated[Literal["nano", "xlarge"], Field(description="YOLO model size.")] = "nano",
    limit: Annotated[int, Field(description="Batch size for pagination.")] = 10,
    offset: Annotated[int, Field(description="Pagination offset. Increment this by 'limit' to see more results.")] = 0,
    fast_mode: Annotated[bool, Field(description="Enabled by default. Set to False for 'Forensic Precision' (full-res analysis, much slower on 40MP+).")] = True
) -> dict:
    """
    Batch analyzes a folder with high concurrency (4-8 images at once).
    Use 'limit' and 'offset' to manage large folders. If 'nextOffset' is present in the response, 
    call this tool again with that offset to continue analysis.
    """
    analytics.track_tool_invocation("photographi_analyze_folder")
    return _analyze_folder_logic(folder_path, metrics, enable_subject_detection, model_size, limit, offset, fast_mode)

@mcp.tool()
def photographi_rank_photographs(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    top_n: Annotated[int, Field(description="Number of top-rated images to return.")] = 1,
    limit: Annotated[int, Field(description="Max images to evaluate in this batch.")] = 50,
    offset: Annotated[int, Field(description="Pagination offset.")] = 0,
    metrics: Annotated[list[str], Field(description="Specific metrics for ranking.")] = None,
    enable_subject_detection: bool = True,
    model_size: Annotated[Literal["nano", "xlarge"], Field(description="YOLO model size.")] = "nano",
    fast_mode: Annotated[bool, Field(description="Enabled by default for responsiveness. Set to False for full-resolution forensic evaluation.")] = True
) -> dict:
    """
    Ranks photos by technical quality using high concurrency.
    Useful for finding the 'best' frame in a high-speed sequence.
    Supports pagination via 'limit' and 'offset' for large sets.
    """
    analytics.track_tool_invocation("photographi_rank_photographs")
    return _rank_folder_logic(folder_path, top_n, limit, offset, metrics, enable_subject_detection, model_size, fast_mode)

@mcp.tool()
def photographi_cull_photographs(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    threshold: Annotated[float, Field(description="Overall score threshold (0.0-1.0). Images below this are culled.")] = 0.4,
    mode: Annotated[Literal["move", "xmp", "both"], Field(description="Cull action (move files or tag XMP).")] = "move",
    enable_subject_detection: bool = True,
    limit: Annotated[int, Field(description="Number of images to cull in this batch.")] = 50,
    offset: Annotated[int, Field(description="Pagination offset.")] = 0,
    fast_mode: Annotated[bool, Field(description="Enabled by default. Fast Mode is recommended for initial sorting.")] = True
) -> dict:
    """
    Filters low-quality images using concurrency.
    Process folders in batches using 'limit' and 'offset'.
    Highly concurrent (4-8 images at once).
    """
    analytics.track_tool_invocation("photographi_cull_photographs")
    return _cull_logic(folder_path, threshold, mode, False, None, enable_subject_detection, "nano", limit, offset, fast_mode)

@mcp.tool()
def photographi_threshold_cull(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    min_confidence: float = 0.6,
    mode: Literal["move", "xmp", "both"] = "move",
    enable_subject_detection: bool = True,
    limit: int = 50,
    offset: int = 0,
    fast_mode: bool = True
) -> dict:
    """Binary threshold culling using concurrency and pagination."""
    analytics.track_tool_invocation("photographi_threshold_cull")
    return _cull_logic(folder_path, min_confidence, mode, True, None, enable_subject_detection, "nano", limit, offset, fast_mode)

@mcp.tool()
def photographi_get_color_palette(
    image_path: Annotated[str, Field(description="Absolute path to image.")],
    colors: int = 5
) -> dict:
    """Extracts a representative color palette using K-Means Clustering."""
    analytics.track_tool_invocation("photographi_get_color_palette")
    palette = generate_color_palette(image_path, colors)
    return {"colors": palette}

@mcp.tool()
def photographi_get_scene_content(
    image_path: Annotated[str, Field(description="Absolute path to RAW/JPEG/TIFF.")]
) -> dict:
    """Returns a clean list of detected objects (e.g., person, dog, car)."""
    analytics.track_tool_invocation("photographi_get_scene_content")
    try:
        objects = detect_objects(image_path)
        return {"objects": objects}
    except Exception as e:
        return {"error": str(e)}

def _bulk_palette_logic(folder_path: str, colors: int = 5, limit: int = 20, offset: int = 0) -> dict:
    """Logic for batch palette extraction."""
    try:
        folder_path = _validate_path(folder_path, expected_type="dir")
    except ValueError as e:
        return {"error": str(e)}
    image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS) and not f.startswith(".")])
    if not image_files: return {"message": "No images found."}
    total_images = len(image_files)
    paginated_files = image_files[offset : offset + limit]
    if not paginated_files: return {"message": "No more images.", "totalImages": total_images}
    
    results = {}
    for filename in paginated_files:
        try:
            results[filename] = generate_color_palette(os.path.join(folder_path, filename), colors)
        except Exception as e:
            results[filename] = {"error": str(e)}
            
    response = {"status": "Complete", "totalImages": total_images, "returned": len(results), "offset": offset, "palettes": results}
    if offset + limit < total_images: response["nextOffset"] = offset + limit
    return response

@mcp.tool()
def photographi_get_folder_palettes(
    folder_path: Annotated[str, Field(description="Absolute path to folder.")],
    colors: int = 5,
    limit: int = 20,
    offset: int = 0
) -> dict:
    """Batch color palette extraction with pagination."""
    analytics.track_tool_invocation("photographi_get_folder_palettes")
    return _bulk_palette_logic(folder_path, colors, limit, offset)

def main():
    parser = argparse.ArgumentParser(description="Photographi MCP Server")
    parser.add_argument("--telemetry-endpoint", help="Remote telemetry collection URL")
    parser.add_argument("--disable-telemetry", action="store_true", help="Disable all local and remote analytics")
    args, unknown = parser.parse_known_args()
    analytics.configure(endpoint=args.telemetry_endpoint, disabled=True if args.disable_telemetry else None)
    mcp.run()

if __name__ == "__main__":
    main()
