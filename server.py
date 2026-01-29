import os
import shutil
import logging
from tqdm import tqdm
from fastmcp import FastMCP
import photo_quality_analyzer_core.analyzer as analyzer
from photo_quality_analyzer_core.analyzer import (
    evaluate_photo_quality,
    load_yolo_model_and_names,
    extract_palette,
    write_xmp_sidecar,
    SUPPORTED_EXTENSIONS,
    YOLO_MODEL_PATH_DEFAULT,
    COCO_NAMES_FILE_PATH_DEFAULT,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("photographi-mcp")

# Initialize MCP server
mcp = FastMCP("photographi")

_initialized = False

def ensure_initialized():
    """Ensures the YOLO model and logic are initialized."""
    global _initialized
    if not _initialized:
        logger.info("Initializing photographi core...")
        # Load the model once
        model, names = load_yolo_model_and_names(
            YOLO_MODEL_PATH_DEFAULT, COCO_NAMES_FILE_PATH_DEFAULT
        )
        analyzer.g_yolo_model = model
        analyzer.g_coco_names = names
        if analyzer.g_yolo_model is None:
            logger.error("Failed to load YOLO model.")
        else:
            logger.info("YOLO model loaded successfully.")
        _initialized = True

def _analyze_photo_logic(image_path: str, metrics: list[str] = None, enable_subject_detection: bool = True) -> dict:
    if not os.path.exists(image_path):
        return {"error": f"File not found: {image_path}"}
    
    try:
        result = evaluate_photo_quality(image_path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection)
        return result
    except Exception as e:
        logger.error(f"Error analyzing {image_path}: {e}")
        return {"error": str(e)}

def _analyze_folder_logic(folder_path: str, metrics: list[str] = None, enable_subject_detection: bool = True) -> dict:
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"error": f"Directory not found: {folder_path}"}
    
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    if not image_files:
        return {"message": "No images found in the folder."}
    
    results = {}
    total_confidence = 0
    
    # Use tqdm for progress indication in the terminal
    for filename in tqdm(image_files, desc="Analyzing folder"):
        image_path = os.path.join(folder_path, filename)
        try:
            result = evaluate_photo_quality(image_path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection)
            results[filename] = {
                "judgement": result["judgement"],
                "overallConfidence": result["overallConfidence"]
            }
            total_confidence += result["overallConfidence"]
        except Exception as e:
            results[filename] = {"error": str(e)}
            
    summary = {
        "totalImages": len(image_files),
        "averageConfidence": total_confidence / len(image_files) if image_files else 0,
        "results": results
    }
    
    return summary

@mcp.tool()
def analyze_photo(image_path: str, metrics: list[str] = None, enable_subject_detection: bool = True) -> dict:
    """
    Analyzes technical quality. Use 'enable_subject_detection=False' for fast mode.
    """
    return _analyze_photo_logic(image_path, metrics, enable_subject_detection)

def _rank_folder_logic(folder_path: str, top_n: int = 10, metrics: list[str] = None, enable_subject_detection: bool = True) -> dict:
    """Logic for ranking folder."""
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"error": f"Directory not found: {folder_path}"}
    
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    if not image_files:
        return {"message": "No images found."}
        
    scored_images = []
    for filename in image_files:
        path = os.path.join(folder_path, filename)
        try:
            res = evaluate_photo_quality(path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection)
            scored_images.append({
                "filename": filename,
                "score": res["overallConfidence"],
                "judgement": res["judgement"]
            })
        except:
            continue
            
    # Sort by score descending
    scored_images.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "totalImages": len(image_files),
        "topN": scored_images[:top_n]
    }

def _cull_folder_logic(folder_path: str, threshold: float = 0.4, keep_best_n: int = None, mode: str = "xmp", metrics: list[str] = None, enable_subject_detection: bool = True) -> dict:
    """
    Advanced culling logic supporting Threshold (Quality) and Quantity (Keep N) targets.
    Modes: 'xmp', 'move', 'both'
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"error": "Directory not found."}
        
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(SUPPORTED_EXTENSIONS)]
    if not image_files:
        return {"message": "No images found."}
        
    # 1. Analyze all images
    scored_images = []
    for filename in tqdm(image_files, desc="Visual intelligence analysis"):
        path = os.path.join(folder_path, filename)
        try:
            res = evaluate_photo_quality(path, requested_metrics=metrics, enable_subject_detection=enable_subject_detection)
            scored_images.append({
                "filename": filename,
                "path": path,
                "score": res["overallConfidence"]
            })
        except Exception as e:
            logger.error(f"Failed to analyze {filename}: {e}")
            continue
            
    # 2. Determine "Rejects"
    rejects = []
    if keep_best_n is not None:
        # Quantity Mode: Sort and pick bottom images
        scored_images.sort(key=lambda x: x["score"], reverse=True)
        # Rejects are everything after the top N
        rejects = scored_images[keep_best_n:]
    else:
        # Threshold Mode: Check quality
        rejects = [img for img in scored_images if img["score"] < threshold]
        
    # 3. Apply Actions
    culled_results = []
    if rejects:
        culled_dir = os.path.join(folder_path, "culled_photos")
        if mode in ["move", "both"] and not os.path.exists(culled_dir):
            os.makedirs(culled_dir)
            
        for img in rejects:
            status_actions = []
            # XMP Action
            if mode in ["xmp", "both"]:
                write_xmp_sidecar(img["path"], rating=0, label="Rejected")
                status_actions.append("XMP-Tagged")
                
            # Move Action
            if mode in ["move", "both"]:
                try:
                    dest = os.path.join(culled_dir, img["filename"])
                    # Also move XMP if it exists
                    xmp_path = os.path.splitext(img["path"])[0] + ".xmp"
                    shutil.move(img["path"], dest)
                    if os.path.exists(xmp_path):
                        shutil.move(xmp_path, os.path.join(culled_dir, os.path.basename(xmp_path)))
                    status_actions.append("Moved")
                except Exception as e:
                    logger.error(f"Failed to move {img['filename']}: {e}")
                    status_actions.append(f"Move-Failed")
                    
            culled_results.append({
                "filename": img["filename"],
                "score": round(img["score"], 2),
                "actions": status_actions
            })
            
    return {
        "totalImages": len(image_files),
        "keepTarget": keep_best_n if keep_best_n else f"Quality > {threshold}",
        "actionMode": mode,
        "culledCount": len(culled_results),
        "culledFiles": culled_results
    }

@mcp.tool()
def analyze_photo(image_path: str, metrics: list[str] = None, enable_subject_detection: bool = True) -> dict:
    """
    Analyzes technical quality. Use 'enable_subject_detection=False' for fast mode.
    """
    return _analyze_photo_logic(image_path, metrics, enable_subject_detection)

@mcp.tool()
def analyze_folder(folder_path: str, metrics: list[str] = None, enable_subject_detection: bool = True) -> dict:
    """
    Analyzes a folder's quality. Use 'enable_subject_detection=False' for fast mode.
    """
    return _analyze_folder_logic(folder_path, metrics, enable_subject_detection)

@mcp.tool()
def rank_folder(folder_path: str, top_n: int = 10, metrics: list[str] = None, enable_subject_detection: bool = True) -> dict:
    """
    Ranks files by quality. Use 'enable_subject_detection=False' for fast mode.
    """
    return _rank_folder_logic(folder_path, top_n, metrics, enable_subject_detection)

@mcp.tool()
def get_color_palette(image_path: str, colors: int = 5) -> dict:
    """
    Extracts the dominant hex color palette from an image.
    """
    ensure_initialized()
    if not os.path.exists(image_path):
        return {"error": "File not found."}
    
    palette = extract_palette(image_path, colors)
    return {"palette": palette}

@mcp.tool()
def cull_folder(folder_path: str, threshold: float = 0.4, keep_best_n: int = None, mode: str = "xmp", metrics: list[str] = None, enable_subject_detection: bool = True) -> dict:
    """
    Culls photos. Use 'enable_subject_detection=False' for fast mode.
    """
    return _cull_folder_logic(folder_path, threshold, keep_best_n, mode, metrics, enable_subject_detection)

if __name__ == "__main__":
    mcp.run()
