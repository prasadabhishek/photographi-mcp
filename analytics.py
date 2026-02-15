# photographi: Privacy-First Analytics Manager
# Part of the photographi visual intelligence engine.
# License: MIT
import os
import json
import logging
import datetime
import platform
import time
from pathlib import Path

logger = logging.getLogger("photographi-analytics")

class AnalyticsManager:
    """
    Privacy-First, Extensive Analytics for photographi.
    Aggregates technical performance and usage metrics locally.
    """
    
    def __init__(self):
        self.home_dir = Path.home() / ".photographi"
        self.telemetry_path = self.home_dir / "telemetry.json"
        
        # Telemetry Relay (Safe for Open Source)
        self.official_relay = "https://photographi-telemetry.abhishek-a-prasad.workers.dev/"
        
        # Configuration
        self.disabled = os.environ.get("PHOTOGRAPHI_TELEMETRY_DISABLED", "0") == "1"
        self.endpoint = os.environ.get("PHOTOGRAPHI_TELEMETRY_ENDPOINT", self.official_relay)

    def configure(self, endpoint: str = None, disabled: bool = None):
        """
        Runtime configuration update.
        Called by server.py after parsing CLI args.
        """
        if disabled is not None:
            self.disabled = disabled
            
        if endpoint:
            self.endpoint = endpoint
            
        # Only initialize file system if explicitly NOT disabled
        if not self.disabled:
             self.home_dir.mkdir(parents=True, exist_ok=True)
             self._ensure_file_exists()
             self._track_environment()

    def _ensure_file_exists(self):
        if not self.telemetry_path.exists():
            initial_data = {
                "first_run": str(datetime.datetime.now()),
                "last_transmission": None,
                "total_images_processed": 0,
                "tool_usage": {},
                "judgement_distribution": {
                    "Excellent": 0, "Good": 0, "Acceptable": 0, "Poor": 0, "Very Poor": 0
                },
                "quality_scores": {
                    "avg_technical": 0,
                    "avg_aesthetic": 0,
                    "avg_overall": 0
                },
                "performance": {
                    "avg_processing_time_ms": 0,
                    "avg_model_load_time_ms": 0,
                    "total_samples": 0
                },
                "environment": {
                    "os": platform.system(),
                    "python": platform.python_version(),
                    "arch": platform.machine()
                },
                "technical": {
                    "formats": {},
                    "model_sizes": {},
                    "cameras": {},
                    "lenses": {},
                    "features": {
                        "subject_detection": 0,
                        "xmp_sidecar": 0,
                        "color_palette": 0
                    }
                },
                "errors": {
                    "total": 0,
                    "types": {}
                }
            }
            self._save_data(initial_data)

    def _load_data(self):
        try:
            with open(self.telemetry_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._ensure_file_exists()
            return self._load_data()

    def _save_data(self, data):
        if self.disabled: return
        try:
            with open(self.telemetry_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save telemetry: {e}")

    def _track_environment(self):
        if self.disabled: return
        data = self._load_data()
        data["environment"] = {
            "os": platform.system(),
            "python": platform.python_version(),
            "arch": platform.machine()
        }
        self._save_data(data)

    def track_tool_invocation(self, tool_name: str):
        if self.disabled: return
        data = self._load_data()
        data["tool_usage"][tool_name] = data["tool_usage"].get(tool_name, 0) + 1
        data["last_run"] = str(datetime.datetime.now())
        self._save_data(data)

    def track_analysis_results(self, judgement: str, format_ext: str = None, model_size: str = None, 
                               technical_score: float = 0, aesthetic_score: float = 0, overall_score: float = 0,
                               camera_make: str = None, camera_model: str = None, lens_model: str = None,
                               count: int = 1):
        if self.disabled: return
        data = self._load_data()
        prev_total = data["total_images_processed"]
        data["total_images_processed"] += count
        new_total = data["total_images_processed"]
        
        # Distributions
        if judgement in data["judgement_distribution"]:
            data["judgement_distribution"][judgement] += count
        
        # Quality score rolling average
        qs = data["quality_scores"]
        if prev_total == 0:
            qs["avg_technical"] = technical_score
            qs["avg_aesthetic"] = aesthetic_score
            qs["avg_overall"] = overall_score
        else:
            qs["avg_technical"] = (qs["avg_technical"] * prev_total + technical_score * count) / new_total
            qs["avg_aesthetic"] = (qs["avg_aesthetic"] * prev_total + aesthetic_score * count) / new_total
            qs["avg_overall"] = (qs["avg_overall"] * prev_total + overall_score * count) / new_total

        tech = data["technical"]
        if format_ext:
            ext = format_ext.lower().strip('.')
            tech["formats"][ext] = tech["formats"].get(ext, 0) + count
            
        if model_size:
            tech["model_sizes"][model_size] = tech["model_sizes"].get(model_size, 0) + count
            
        if camera_make and camera_model:
            cam = f"{camera_make} {camera_model}".strip()
            tech["cameras"][cam] = tech["cameras"].get(cam, 0) + count
        elif camera_model:
            tech["cameras"][camera_model] = tech["cameras"].get(camera_model, 0) + count
            
        if lens_model:
            tech["lenses"][lens_model] = tech["lenses"].get(lens_model, 0) + count
            
        self._save_data(data)

    def track_performance(self, proc_time_ms: float, load_time_ms: float = 0):
        if self.disabled: return
        data = self._load_data()
        perf = data["performance"]
        total = perf["total_samples"]
        
        # Rolling average
        if total == 0:
            perf["avg_processing_time_ms"] = proc_time_ms
            perf["avg_model_load_time_ms"] = load_time_ms
        else:
            perf["avg_processing_time_ms"] = (perf["avg_processing_time_ms"] * total + proc_time_ms) / (total + 1)
            if load_time_ms > 0:
                perf["avg_model_load_time_ms"] = (perf["avg_model_load_time_ms"] * total + load_time_ms) / (total + 1)
        
        perf["total_samples"] += 1
        self._save_data(data)

    def track_feature_usage(self, feature: str):
        if self.disabled: return
        data = self._load_data()
        if feature in data["technical"]["features"]:
            data["technical"]["features"][feature] += 1
        self._save_data(data)

    def track_error(self, error_type: str = "Unknown"):
        if self.disabled: return
        data = self._load_data()
        data["errors"]["total"] += 1
        data["errors"]["types"][error_type] = data["errors"]["types"].get(error_type, 0) + 1
        self._save_data(data)

    def transmit_telemetry(self):
        if self.disabled or not self.endpoint: return
        data = self._load_data()
        now = str(datetime.datetime.now())
        
        # We transform the aggregate state into a "Batch of Events" for Axiom.
        # This prevents the 256-field limit by using stable column names.
        events = []
        
        # 1. Global State Event
        global_event = {
            "event_type": "global_state",
            "timestamp": now,
            "total_images_processed": data.get("total_images_processed", 0),
            "environment": data.get("environment", {}),
            "performance": data.get("performance", {}),
            "quality_scores": data.get("quality_scores", {}),
            "error_total": data.get("errors", {}).get("total", 0)
        }
        events.append(global_event)
        
        # 2. Distribution Events (Label/Value pattern)
        distributions = [
            ("camera", data.get("technical", {}).get("cameras", {})),
            ("lens", data.get("technical", {}).get("lenses", {})),
            ("format", data.get("technical", {}).get("formats", {})),
            ("tool", data.get("tool_usage", {})),
            ("judgement", data.get("judgement_distribution", {})),
            ("model_size", data.get("technical", {}).get("model_sizes", {})),
            ("error_type", data.get("errors", {}).get("types", {})),
            ("feature", data.get("technical", {}).get("features", {}))
        ]
        
        for category, mapping in distributions:
            for label, value in mapping.items():
                events.append({
                    "event_type": "distribution",
                    "category": category,
                    "label": str(label),
                    "value": value,
                    "timestamp": now
                })
        
        try:
            import requests
            # Axiom handles JSON arrays as batches of events
            response = requests.post(self.endpoint, json=events, timeout=5)
            if response.status_code in [200, 201]:
                data["last_transmission"] = now
                self._save_data(data)
                logger.debug(f"Transmitted {len(events)} events to Axiom.")
        except Exception as e:
            logger.debug(f"Telemetry transmission skipped: {e}")

    def get_summary(self):
        if self.disabled: return {"status": "telemetry disabled"}
        return self._load_data()

analytics = AnalyticsManager()
