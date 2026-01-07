"""
Defense Coordinator Module for AI Defense Container
Orchestrates all defense systems and coordinates responses.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import os

from .anomaly_detector import AnomalyDetector
from .threat_analyzer import ThreatAnalyzer
from .neural_monitor import NeuralMonitor

logger = logging.getLogger(__name__)

class DefenseCoordinator:
    """Coordinates all AI defense systems"""

    def __init__(self):
        self.status = "initializing"
        self.defense_systems = {}
        self.alerts = []
        self.defense_history = []
        self.coordination_config = {
            "monitoring_interval": 30,  # seconds
            "alert_threshold": 0.7,     # confidence threshold
            "auto_response": True,
            "max_alerts_per_hour": 10
        }

        # Initialize defense systems
        self._initialize_defense_systems()

        self.status = "ready"
        logger.info("Defense coordinator initialized")

    def _initialize_defense_systems(self):
        """Initialize all defense system components"""
        try:
            self.defense_systems = {
                "anomaly_detector": AnomalyDetector(),
                "threat_analyzer": ThreatAnalyzer(),
                "neural_monitor": NeuralMonitor()
            }
            logger.info("All defense systems initialized")
        except Exception as e:
            logger.error(f"Failed to initialize defense systems: {e}")
            self.defense_systems = {}

    async def start_defense_monitoring(self) -> Dict[str, Any]:
        """Start continuous defense monitoring"""
        try:
            logger.info("Starting defense monitoring cycle")

            while True:
                # Run monitoring cycle
                await self._run_monitoring_cycle()

                # Check for alerts and coordinate responses
                await self._process_alerts()

                # Wait for next cycle
                await asyncio.sleep(self.coordination_config["monitoring_interval"])

        except Exception as e:
            logger.error(f"Defense monitoring failed: {e}")
            return {"error": str(e)}

    async def _run_monitoring_cycle(self):
        """Execute one complete monitoring cycle"""
        try:
            cycle_start = datetime.utcnow()

            # Run all defense systems
            results = {}
            for system_name, system in self.defense_systems.items():
                try:
                    if hasattr(system, 'check_model_performance'):
                        results[system_name] = await system.check_model_performance()
                    elif hasattr(system, 'analyze_recent_activity'):
                        results[system_name] = await system.analyze_recent_activity()
                    elif hasattr(system, 'scan_for_anomalies'):
                        results[system_name] = await system.scan_for_anomalies()
                    else:
                        results[system_name] = {"status": "no_monitoring_method"}
                except Exception as e:
                    logger.error(f"Error in {system_name}: {e}")
                    results[system_name] = {"error": str(e)}

            # Record cycle results
            cycle_result = {
                "timestamp": cycle_start.isoformat(),
                "duration": (datetime.utcnow() - cycle_start).total_seconds(),
                "results": results,
                "alerts_generated": 0
            }

            self.defense_history.append(cycle_result)

            # Keep only last 100 cycles
            if len(self.defense_history) > 100:
                self.defense_history = self.defense_history[-100:]

            logger.debug(f"Monitoring cycle completed in {cycle_result['duration']:.2f}s")

        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}")

    async def _process_alerts(self):
        """Process and coordinate responses to alerts"""
        try:
            # Check for new alerts from all systems
            new_alerts = []

            for system_name, system in self.defense_systems.items():
                try:
                    if hasattr(system, 'get_alerts'):
                        system_alerts = await system.get_alerts()
                        for alert in system_alerts:
                            if alert.get("confidence", 0) > self.coordination_config["alert_threshold"]:
                                alert["system"] = system_name
                                alert["coordinated_at"] = datetime.utcnow().isoformat()
                                new_alerts.append(alert)
                except Exception as e:
                    logger.error(f"Error getting alerts from {system_name}: {e}")

            # Filter alerts based on rate limiting
            filtered_alerts = self._filter_alerts(new_alerts)

            # Add to alert queue
            self.alerts.extend(filtered_alerts)

            # Keep only recent alerts
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.alerts = [a for a in self.alerts if datetime.fromisoformat(a["timestamp"]) > cutoff_time]

            # Coordinate responses if auto-response is enabled
            if self.coordination_config["auto_response"] and filtered_alerts:
                await self._coordinate_responses(filtered_alerts)

            # Update cycle results with alert count
            if self.defense_history:
                self.defense_history[-1]["alerts_generated"] = len(filtered_alerts)

        except Exception as e:
            logger.error(f"Alert processing failed: {e}")

    def _filter_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter alerts based on rate limiting and deduplication"""
        # Simple rate limiting: max alerts per hour
        recent_alerts = [a for a in self.alerts if datetime.fromisoformat(a["timestamp"]) > datetime.utcnow() - timedelta(hours=1)]

        if len(recent_alerts) >= self.coordination_config["max_alerts_per_hour"]:
            logger.warning("Alert rate limit exceeded, filtering alerts")
            return []

        # Deduplicate similar alerts (same type within last 5 minutes)
        filtered = []
        for alert in alerts:
            is_duplicate = False
            for existing in recent_alerts[-10:]:  # Check last 10 alerts
                if (alert.get("type") == existing.get("type") and
                    datetime.fromisoformat(alert["timestamp"]) - datetime.fromisoformat(existing["timestamp"]) < timedelta(minutes=5)):
                    is_duplicate = True
                    break

            if not is_duplicate:
                filtered.append(alert)

        return filtered

    async def _coordinate_responses(self, alerts: List[Dict[str, Any]]):
        """Coordinate automated responses to alerts"""
        try:
            for alert in alerts:
                response_actions = self._determine_response_actions(alert)

                for action in response_actions:
                    await self._execute_response_action(action, alert)

                logger.info(f"Coordinated response for alert: {alert.get('type', 'unknown')}")

        except Exception as e:
            logger.error(f"Response coordination failed: {e}")

    def _determine_response_actions(self, alert: Dict[str, Any]) -> List[str]:
        """Determine appropriate response actions for an alert"""
        actions = []

        alert_type = alert.get("type", "")
        confidence = alert.get("confidence", 0)

        if confidence > 0.9:
            # High confidence alerts get immediate action
            if "anomaly" in alert_type.lower():
                actions.extend(["isolate_resource", "increase_monitoring"])
            elif "threat" in alert_type.lower():
                actions.extend(["block_access", "log_incident"])
            elif "performance" in alert_type.lower():
                actions.extend(["scale_resources", "trigger_upgrade"])

        elif confidence > 0.7:
            # Medium confidence alerts get monitoring action
            actions.append("increase_monitoring")

        return actions

    async def _execute_response_action(self, action: str, alert: Dict[str, Any]):
        """Execute a specific response action"""
        try:
            # Simulate response execution
            await asyncio.sleep(0.1)  # Simulate action time

            response_record = {
                "action": action,
                "alert_id": alert.get("id", "unknown"),
                "timestamp": datetime.utcnow().isoformat(),
                "status": "executed"
            }

            logger.info(f"Executed response action: {action} for alert {alert.get('id', 'unknown')}")

            # In a real implementation, this would trigger actual defense actions
            # like API calls to security systems, resource scaling, etc.

        except Exception as e:
            logger.error(f"Failed to execute response action {action}: {e}")

    async def get_defense_status(self) -> Dict[str, Any]:
        """Get comprehensive defense system status"""
        try:
            system_statuses = {}
            for system_name, system in self.defense_systems.items():
                try:
                    if hasattr(system, 'get_status'):
                        system_statuses[system_name] = await system.get_status()
                    else:
                        system_statuses[system_name] = {"status": "unknown"}
                except Exception as e:
                    system_statuses[system_name] = {"error": str(e)}

            return {
                "coordinator_status": self.status,
                "systems": system_statuses,
                "active_alerts": len(self.alerts),
                "recent_cycles": len(self.defense_history),
                "configuration": self.coordination_config,
                "last_cycle": self.defense_history[-1] if self.defense_history else None
            }

        except Exception as e:
            logger.error(f"Failed to get defense status: {e}")
            return {"error": str(e)}

    async def update_configuration(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update defense coordination configuration"""
        try:
            for key, value in config_updates.items():
                if key in self.coordination_config:
                    self.coordination_config[key] = value
                    logger.info(f"Updated configuration: {key} = {value}")

            return {
                "updated": True,
                "configuration": self.coordination_config
            }

        except Exception as e:
            logger.error(f"Configuration update failed: {e}")
            return {"error": str(e), "updated": False}

    async def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alert history for specified time period"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_alerts = [a for a in self.alerts if datetime.fromisoformat(a["timestamp"]) > cutoff_time]

            return recent_alerts

        except Exception as e:
            logger.error(f"Failed to get alert history: {e}")
            return []

    async def manual_response(self, alert_id: str, action: str) -> Dict[str, Any]:
        """Execute manual response action for specific alert"""
        try:
            # Find the alert
            alert = None
            for a in self.alerts:
                if a.get("id") == alert_id:
                    alert = a
                    break

            if not alert:
                return {"error": "Alert not found", "executed": False}

            # Execute the action
            await self._execute_response_action(action, alert)

            return {
                "executed": True,
                "alert_id": alert_id,
                "action": action,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Manual response failed: {e}")
            return {"error": str(e), "executed": False}