"""Thread-safe performance telemetry and latency metrics tracker."""

import threading


class TelemetryTracker:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        self._lock = threading.Lock()
        self.search_count: int = 0
        self.hit_count: int = 0
        self.miss_count: int = 0

        self.total_det_time: float = 0.0
        self.total_emb_time: float = 0.0
        self.total_search_time: float = 0.0
        self.total_api_time: float = 0.0

        self._initialized = True

    def record_search(
        self,
        hit: bool,
        detection_ms: float,
        embedding_ms: float,
        search_ms: float,
        total_api_ms: float,
    ) -> None:
        """Atomically record search outcomes and micro-latencies."""
        with self._lock:
            self.search_count += 1
            if hit:
                self.hit_count += 1
            else:
                self.miss_count += 1

            self.total_det_time += detection_ms
            self.total_emb_time += embedding_ms
            self.total_search_time += search_ms
            self.total_api_time += total_api_ms

    def get_metrics(self) -> dict:
        """Computes and returns aggregated averages and hit rates."""
        with self._lock:
            cnt = max(self.search_count, 1)
            hit_rate = (self.hit_count / cnt) if self.search_count > 0 else 0.0

            return {
                "total_searches": self.search_count,
                "hits": self.hit_count,
                "misses": self.miss_count,
                "hit_rate": float(f"{hit_rate:.4f}"),
                "average_latencies_ms": {
                    "face_detection": (
                        float(f"{(self.total_det_time / cnt):.2f}")
                        if self.search_count > 0
                        else 0.0
                    ),
                    "embedding_generation": (
                        float(f"{(self.total_emb_time / cnt):.2f}")
                        if self.search_count > 0
                        else 0.0
                    ),
                    "faiss_search": (
                        float(f"{(self.total_search_time / cnt):.2f}")
                        if self.search_count > 0
                        else 0.0
                    ),
                    "total_api_response": (
                        float(f"{(self.total_api_time / cnt):.2f}")
                        if self.search_count > 0
                        else 0.0
                    ),
                },
            }
