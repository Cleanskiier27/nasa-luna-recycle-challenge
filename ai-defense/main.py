#!/usr/bin/env python3
"""
AI Defense Container - NetworkBuster Primary Repository Defense System
Provides AI-powered security, monitoring, and threat detection for the main repository.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Import defense modules
from .anomaly_detector import AnomalyDetector
from .threat_analyzer import ThreatAnalyzer
from .neural_monitor import NeuralMonitor
from .defense_coordinator import DefenseCoordinator
from .azure_storage_defense import AzureStorageDefense

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/ai-defense.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AIDefenseContainer:
    """Main AI Defense Container class"""

    def __init__(self):
        self.app = FastAPI(title="AI Defense Container", version="2.0.0")
        self.defense_level = os.getenv("DEFENSE_LEVEL", "maximum")
        self.monitoring_interval = int(os.getenv("MONITORING_INTERVAL", "30"))

        # Initialize defense systems
        self.anomaly_detector = AnomalyDetector()
        self.threat_analyzer = ThreatAnalyzer()
        self.neural_monitor = NeuralMonitor()
        self.defense_coordinator = DefenseCoordinator()
        self.azure_defense = AzureStorageDefense()

        # Setup middleware
        self._setup_middleware()

        # Setup routes
        self._setup_routes()

        # Defense state
        self.defense_active = False
        self.last_scan = None
        self.threats_detected = 0
        self.defenses_activated = 0

    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "defense_active": self.defense_active,
                "timestamp": datetime.utcnow().isoformat(),
                "version": "2.0.0"
            }

        @self.app.get("/status")
        async def get_status():
            return {
                "defense_level": self.defense_level,
                "monitoring_interval": self.monitoring_interval,
                "threats_detected": self.threats_detected,
                "defenses_activated": self.defenses_activated,
                "last_scan": self.last_scan,
                "systems_status": {
                    "anomaly_detector": self.anomaly_detector.status,
                    "threat_analyzer": self.threat_analyzer.status,
                    "neural_monitor": self.neural_monitor.status,
                    "azure_defense": self.azure_defense.status
                }
            }

        @self.app.post("/activate-defense")
        async def activate_defense(background_tasks: BackgroundTasks):
            """Activate AI defense systems"""
            if not self.defense_active:
                self.defense_active = True
                background_tasks.add_task(self._start_defense_loop)
                logger.info("AI Defense systems activated")
                return {"message": "AI Defense activated", "status": "active"}
            return {"message": "AI Defense already active", "status": "active"}

        @self.app.post("/scan-repository")
        async def scan_repository():
            """Perform comprehensive repository scan"""
            try:
                # Use defense coordinator for comprehensive scan
                results = await self.defense_coordinator.get_defense_status()
                self.last_scan = datetime.utcnow().isoformat()

                # Count threats from recent alerts
                recent_alerts = await self.defense_coordinator.get_alert_history(hours=1)
                self.threats_detected += len(recent_alerts)

                return {
                    "scan_complete": True,
                    "timestamp": self.last_scan,
                    "results": results,
                    "alerts_found": len(recent_alerts)
                }
            except Exception as e:
                logger.error(f"Repository scan failed: {e}")
                return {"error": str(e), "scan_complete": False}

        @self.app.post("/analyze-threat/{threat_id}")
        async def analyze_threat(threat_id: str):
            """Analyze specific threat"""
            try:
                analysis = await self.threat_analyzer.analyze_threat(threat_id)
                return {"threat_id": threat_id, "analysis": analysis}
            except Exception as e:
                logger.error(f"Threat analysis failed: {e}")
                return {"error": str(e)}

        @self.app.get("/neural-status")
        async def get_neural_status():
            """Get neural network status"""
            return await self.neural_monitor.get_status()

        @self.app.post("/upgrade-neural-network")
        async def upgrade_neural_network():
            """Upgrade neural network models"""
            try:
                result = await self.neural_monitor.upgrade_models()
                return {"upgrade_complete": True, "result": result}
            except Exception as e:
                logger.error(f"Neural network upgrade failed: {e}")
                return {"error": str(e), "upgrade_complete": False}

        @self.app.get("/defense-status")
        async def get_defense_status():
            """Get comprehensive defense system status"""
            return await self.defense_coordinator.get_defense_status()

        @self.app.get("/alerts")
        async def get_alerts(hours: int = 24):
            """Get recent alerts"""
            return await self.defense_coordinator.get_alert_history(hours)

        @self.app.post("/manual-response")
        async def manual_response(alert_id: str, action: str):
            """Execute manual response action"""
            return await self.defense_coordinator.manual_response(alert_id, action)

        @self.app.get("/storage-status")
        async def get_storage_status():
            """Get Azure Storage defense status"""
            return await self.azure_defense.get_storage_status()

        @self.app.post("/backup-models")
        async def backup_models():
            """Backup AI defense models"""
            try:
                # Get current model states
                models_data = {
                    "anomaly_detector": await self.anomaly_detector.get_status(),
                    "threat_analyzer": await self.threat_analyzer.get_status(),
                    "neural_monitor": await self.neural_monitor.get_status(),
                    "backup_timestamp": datetime.utcnow().isoformat()
                }

                success = await self.azure_defense.backup_defense_models(models_data)
                return {"backup_complete": success}
            except Exception as e:
                logger.error(f"Model backup failed: {e}")
                return {"error": str(e), "backup_complete": False}

    async def _start_defense_loop(self):
        """Main defense monitoring loop"""
        logger.info("Starting AI defense monitoring loop")

        while self.defense_active:
            try:
                # Perform continuous monitoring
                await self._perform_monitoring_cycle()
                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Defense monitoring error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry

    async def _perform_monitoring_cycle(self):
        """Perform one monitoring cycle"""
        try:
            # Use defense coordinator for comprehensive monitoring
            cycle_result = await self.defense_coordinator._run_monitoring_cycle()

            # Process alerts through coordinator
            await self.defense_coordinator._process_alerts()

            # Get alert count for metrics
            recent_alerts = await self.defense_coordinator.get_alert_history(hours=1)
            alert_count = len(recent_alerts)

            if alert_count > 0:
                logger.warning(f"Alerts detected in cycle: {alert_count}")
                self.threats_detected += alert_count
                self.defenses_activated += 1

            # Store defense metrics in Azure
            metrics = {
                "cycle_timestamp": datetime.utcnow().isoformat(),
                "alerts_detected": alert_count,
                "systems_status": await self.defense_coordinator.get_defense_status(),
                "neural_performance": await self.neural_monitor.check_model_performance()
            }

            await self.azure_defense.store_defense_metrics(metrics)

        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}")

    async def shutdown(self):
        """Shutdown defense systems"""
        logger.info("Shutting down AI Defense systems")
        self.defense_active = False

        # Note: Individual system shutdown methods would be called here if they existed
        # For now, just log the shutdown


def main():
    """Main entry point"""
    defense_container = AIDefenseContainer()

    # Setup shutdown handler
    async def shutdown_handler():
        await defense_container.shutdown()

    # Add shutdown event handler
    import signal
    loop = asyncio.get_event_loop()

    def signal_handler():
        loop.create_task(shutdown_handler())

    signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
    signal.signal(signal.SIGINT, lambda s, f: signal_handler())

    # Start server
    logger.info("Starting AI Defense Container on port 8000")
    uvicorn.run(
        defense_container.app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()