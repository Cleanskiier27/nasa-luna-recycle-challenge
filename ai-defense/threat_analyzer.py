"""
Threat Analysis Module for AI Defense Container
Analyzes potential security threats and coordinates defense responses.
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import hashlib
import os

logger = logging.getLogger(__name__)

class ThreatAnalyzer:
    """AI-powered threat analysis and response coordination"""

    def __init__(self):
        self.status = "initializing"
        self.threat_patterns = self._load_threat_patterns()
        self.known_threats = set()
        self.active_threats = {}
        self.threat_history = []

        self.status = "ready"
        logger.info("Threat analyzer initialized")

    def _load_threat_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load known threat patterns and signatures"""
        return {
            "suspicious_file_access": {
                "pattern": r"\.env|config\.json|secrets\.|private_key",
                "severity": "high",
                "description": "Access to sensitive configuration files"
            },
            "unusual_network_activity": {
                "pattern": r"(?i)(sql_injection|script|iframe|onload)",
                "severity": "high",
                "description": "Potential injection or XSS attempts"
            },
            "brute_force_attempt": {
                "threshold": 10,  # Failed attempts per minute
                "severity": "medium",
                "description": "Multiple failed authentication attempts"
            },
            "data_exfiltration": {
                "pattern": r"(?i)(download|export|backup).*large_file",
                "severity": "high",
                "description": "Potential data exfiltration attempt"
            },
            "privilege_escalation": {
                "pattern": r"(?i)(sudo|admin|root|su)",
                "severity": "critical",
                "description": "Attempted privilege escalation"
            }
        }

    async def analyze_recent_activity(self) -> List[Dict[str, Any]]:
        """Analyze recent system activity for threats"""
        try:
            threats = []

            # Check log files for suspicious patterns
            log_threats = await self._analyze_logs()
            threats.extend(log_threats)

            # Check network activity
            network_threats = await self._analyze_network_activity()
            threats.extend(network_threats)

            # Check file system changes
            filesystem_threats = await self._analyze_filesystem_changes()
            threats.extend(filesystem_threats)

            # Update active threats
            for threat in threats:
                threat_id = threat["id"]
                if threat_id not in self.active_threats:
                    self.active_threats[threat_id] = threat
                    self.threat_history.append(threat)

            return threats

        except Exception as e:
            logger.error(f"Threat analysis failed: {e}")
            return []

    async def _analyze_logs(self) -> List[Dict[str, Any]]:
        """Analyze log files for threat patterns"""
        threats = []

        try:
            log_files = [
                "/app/logs/ai-defense.log",
                "/var/log/syslog",
                "/var/log/auth.log"
            ]

            for log_file in log_files:
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()[-100:]  # Last 100 lines

                        for line_no, line in enumerate(lines):
                            threat = self._check_line_for_threats(line, log_file, line_no)
                            if threat:
                                threats.append(threat)

        except Exception as e:
            logger.error(f"Log analysis failed: {e}")

        return threats

    def _check_line_for_threats(self, line: str, source: str, line_no: int) -> Optional[Dict[str, Any]]:
        """Check a log line for threat patterns"""
        for threat_type, pattern_info in self.threat_patterns.items():
            pattern = pattern_info.get("pattern")
            if pattern and re.search(pattern, line, re.IGNORECASE):
                threat_id = hashlib.md5(f"{threat_type}_{line}_{datetime.utcnow().timestamp()}".encode()).hexdigest()[:8]

                return {
                    "id": threat_id,
                    "type": threat_type,
                    "severity": pattern_info["severity"],
                    "description": pattern_info["description"],
                    "source": source,
                    "line_number": line_no,
                    "matched_content": line.strip()[:200],  # First 200 chars
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "detected"
                }

        return None

    async def _analyze_network_activity(self) -> List[Dict[str, Any]]:
        """Analyze network activity for threats"""
        threats = []

        try:
            # Simulate network analysis
            # In production, would monitor actual network traffic
            suspicious_connections = [
                {"ip": "192.168.1.100", "port": 22, "attempts": 15},
                {"ip": "10.0.0.50", "port": 80, "attempts": 200}
            ]

            for conn in suspicious_connections:
                if conn["attempts"] > 10:  # Threshold for brute force
                    threat_id = hashlib.md5(f"network_{conn['ip']}_{conn['port']}_{datetime.utcnow().timestamp()}".encode()).hexdigest()[:8]

                    threats.append({
                        "id": threat_id,
                        "type": "brute_force_attempt",
                        "severity": "medium",
                        "description": f"Multiple connection attempts from {conn['ip']}:{conn['port']}",
                        "source": "network_monitor",
                        "details": conn,
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "detected"
                    })

        except Exception as e:
            logger.error(f"Network analysis failed: {e}")

        return threats

    async def _analyze_filesystem_changes(self) -> List[Dict[str, Any]]:
        """Analyze filesystem changes for threats"""
        threats = []

        try:
            # Check for suspicious file modifications
            sensitive_files = [
                "/app/models/",
                "/app/config/",
                "/app/secrets/"
            ]

            for path in sensitive_files:
                if os.path.exists(path):
                    # Check for recent modifications
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                stat = os.stat(file_path)
                                modified_time = datetime.fromtimestamp(stat.st_mtime)

                                # Check if modified in last hour
                                if datetime.utcnow() - modified_time < timedelta(hours=1):
                                    threat_id = hashlib.md5(f"filesystem_{file_path}_{modified_time.timestamp()}".encode()).hexdigest()[:8]

                                    threats.append({
                                        "id": threat_id,
                                        "type": "suspicious_file_access",
                                        "severity": "medium",
                                        "description": f"Recent modification to sensitive file: {file_path}",
                                        "source": "filesystem_monitor",
                                        "file_path": file_path,
                                        "modified_time": modified_time.isoformat(),
                                        "timestamp": datetime.utcnow().isoformat(),
                                        "status": "detected"
                                    })

                            except Exception as e:
                                logger.error(f"Failed to check file {file_path}: {e}")

        except Exception as e:
            logger.error(f"Filesystem analysis failed: {e}")

        return threats

    async def analyze_threat(self, threat_id: str) -> Dict[str, Any]:
        """Perform detailed analysis of a specific threat"""
        try:
            threat = self.active_threats.get(threat_id)
            if not threat:
                return {"error": "Threat not found"}

            # Perform detailed analysis
            analysis = {
                "threat_id": threat_id,
                "risk_assessment": self._assess_risk(threat),
                "recommended_actions": self._get_recommended_actions(threat),
                "similar_threats": self._find_similar_threats(threat),
                "timeline": self._build_threat_timeline(threat),
                "confidence_score": self._calculate_confidence(threat)
            }

            return analysis

        except Exception as e:
            logger.error(f"Threat analysis failed for {threat_id}: {e}")
            return {"error": str(e)}

    def _assess_risk(self, threat: Dict[str, Any]) -> str:
        """Assess the risk level of a threat"""
        severity = threat.get("severity", "low")
        risk_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}

        base_risk = risk_scores.get(severity, 1)

        # Adjust based on threat type and context
        if threat["type"] == "privilege_escalation":
            base_risk += 2
        elif threat["type"] in ["suspicious_file_access", "data_exfiltration"]:
            base_risk += 1

        if base_risk >= 4:
            return "critical"
        elif base_risk >= 3:
            return "high"
        elif base_risk >= 2:
            return "medium"
        else:
            return "low"

    def _get_recommended_actions(self, threat: Dict[str, Any]) -> List[str]:
        """Get recommended actions for a threat"""
        actions = []

        threat_type = threat.get("type")

        if threat_type == "brute_force_attempt":
            actions.extend([
                "Implement rate limiting",
                "Enable account lockout",
                "Review authentication logs",
                "Consider IP blocking"
            ])
        elif threat_type == "suspicious_file_access":
            actions.extend([
                "Audit file permissions",
                "Review access logs",
                "Implement file integrity monitoring",
                "Consider encryption for sensitive files"
            ])
        elif threat_type == "privilege_escalation":
            actions.extend([
                "Immediate security audit",
                "Revoke suspicious privileges",
                "Implement principle of least privilege",
                "Enable detailed audit logging"
            ])

        actions.append("Monitor for similar activity")
        actions.append("Update security policies if needed")

        return actions

    def _find_similar_threats(self, threat: Dict[str, Any]) -> List[str]:
        """Find similar threats in history"""
        similar = []
        threat_type = threat.get("type")

        for historical_threat in self.threat_history[-50:]:  # Last 50 threats
            if historical_threat["type"] == threat_type:
                similar.append(historical_threat["id"])

        return similar[-5:]  # Return last 5 similar threats

    def _build_threat_timeline(self, threat: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build a timeline of threat-related events"""
        timeline = []

        # Add detection event
        timeline.append({
            "event": "threat_detected",
            "timestamp": threat["timestamp"],
            "description": f"Threat {threat['id']} detected"
        })

        # Add analysis event
        timeline.append({
            "event": "analysis_complete",
            "timestamp": datetime.utcnow().isoformat(),
            "description": "Automated threat analysis completed"
        })

        return timeline

    def _calculate_confidence(self, threat: Dict[str, Any]) -> float:
        """Calculate confidence score for threat detection"""
        base_confidence = 0.5

        # Adjust based on severity and evidence
        if threat.get("severity") == "critical":
            base_confidence += 0.3
        elif threat.get("severity") == "high":
            base_confidence += 0.2
        elif threat.get("severity") == "medium":
            base_confidence += 0.1

        # Adjust based on source reliability
        if threat.get("source") in ["filesystem_monitor", "network_monitor"]:
            base_confidence += 0.1

        return min(base_confidence, 1.0)

    async def shutdown(self):
        """Shutdown threat analyzer"""
        self.status = "shutdown"
        logger.info("Threat analyzer shutdown")