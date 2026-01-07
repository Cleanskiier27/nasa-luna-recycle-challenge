"""
Anomaly Detection Module for AI Defense Container
Detects unusual patterns and potential security threats in repository activity.
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import joblib
import os

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """AI-powered anomaly detection for repository security"""

    def __init__(self):
        self.status = "initializing"
        self.model_path = "/app/models/anomaly_detector.pkl"
        self.baseline_data = []
        self.anomaly_threshold = float(os.getenv("ANOMALY_THRESHOLD", "0.85"))
        self.is_trained = False

        # Initialize or load model
        self._initialize_model()

    def _initialize_model(self):
        """Initialize or load the anomaly detection model"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.is_trained = True
                logger.info("Loaded existing anomaly detection model")
            else:
                # Create baseline model
                self.model = self._create_baseline_model()
                logger.info("Created new anomaly detection model")

            self.status = "ready"
        except Exception as e:
            logger.error(f"Failed to initialize anomaly detector: {e}")
            self.status = "error"

    def _create_baseline_model(self):
        """Create a baseline anomaly detection model"""
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler

        # Create sample baseline data
        baseline_features = self._generate_baseline_features()

        # Train model
        model = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )

        if len(baseline_features) > 0:
            model.fit(baseline_features)

        return model

    def _generate_baseline_features(self) -> List[List[float]]:
        """Generate baseline features for normal repository activity"""
        # Simulate normal repository activity patterns
        features = []

        # File access patterns
        for _ in range(100):
            features.append([
                np.random.normal(50, 10),  # File size
                np.random.normal(100, 20), # Access frequency
                np.random.normal(0.1, 0.05), # Error rate
                np.random.normal(10, 3),   # Response time
                np.random.normal(5, 2),    # Concurrent users
            ])

        return features

    async def scan_for_anomalies(self) -> List[Dict[str, Any]]:
        """Scan for anomalies in current repository activity"""
        try:
            # Collect current activity metrics
            current_metrics = await self._collect_current_metrics()

            if not current_metrics:
                return []

            # Predict anomalies
            predictions = self.model.predict(current_metrics)
            scores = self.model.score_samples(current_metrics)

            # Identify anomalies
            anomalies = []
            for i, (prediction, score) in enumerate(zip(predictions, scores)):
                if prediction == -1 or score < -self.anomaly_threshold:
                    anomaly = {
                        "id": f"anomaly_{datetime.utcnow().timestamp()}_{i}",
                        "type": "anomaly_detected",
                        "severity": "high" if score < -0.9 else "medium",
                        "confidence": abs(score),
                        "timestamp": datetime.utcnow().isoformat(),
                        "metrics": current_metrics[i],
                        "description": self._describe_anomaly(current_metrics[i], score)
                    }
                    anomalies.append(anomaly)

            if anomalies:
                logger.warning(f"Detected {len(anomalies)} anomalies")

            return anomalies

        except Exception as e:
            logger.error(f"Anomaly scan failed: {e}")
            return []

    async def _collect_current_metrics(self) -> List[List[float]]:
        """Collect current repository activity metrics"""
        try:
            # Simulate collecting real metrics
            # In production, this would monitor actual repository activity
            metrics = []

            # File system metrics
            file_count = len([f for f in os.listdir('/app') if os.path.isfile(os.path.join('/app', f))])
            dir_count = len([d for d in os.listdir('/app') if os.path.isdir(os.path.join('/app', d))])

            # Network activity (simulated)
            network_requests = np.random.normal(100, 15)
            error_rate = np.random.normal(0.02, 0.01)
            response_time = np.random.normal(50, 10)
            cpu_usage = np.random.normal(30, 8)

            metrics.append([
                float(file_count),
                float(dir_count),
                network_requests,
                error_rate,
                response_time,
                cpu_usage
            ])

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return []

    def _describe_anomaly(self, metrics: List[float], score: float) -> str:
        """Generate description for detected anomaly"""
        descriptions = []

        if metrics[0] > 100:  # High file count
            descriptions.append("Unusual number of files accessed")
        if metrics[3] > 0.1:  # High error rate
            descriptions.append("Elevated error rate detected")
        if metrics[4] > 100:  # Slow response time
            descriptions.append("Abnormally slow response times")
        if abs(score) > 0.95:
            descriptions.append("Highly anomalous activity pattern")

        return "; ".join(descriptions) if descriptions else "Unusual activity pattern detected"

    async def update_baseline(self, new_data: List[List[float]]):
        """Update the anomaly detection baseline with new data"""
        try:
            if len(new_data) > 10:  # Minimum data requirement
                self.model = self._create_baseline_model()
                # In production, would retrain with combined old + new data
                logger.info("Updated anomaly detection baseline")
        except Exception as e:
            logger.error(f"Failed to update baseline: {e}")

    async def shutdown(self):
        """Shutdown anomaly detector"""
        try:
            if hasattr(self, 'model') and self.is_trained:
                joblib.dump(self.model, self.model_path)
                logger.info("Saved anomaly detection model")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")

        self.status = "shutdown"