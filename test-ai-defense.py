#!/usr/bin/env python3
"""
Test script for AI Defense Container
Validates that all modules can be imported and initialized.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add ai-defense directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai-defense'))

async def test_ai_defense_systems():
    """Test all AI defense systems"""
    print("🛡️ Testing AI Defense Container Systems")
    print("=" * 50)

    try:
        # Import all modules
        from anomaly_detector import AnomalyDetector
        from threat_analyzer import ThreatAnalyzer
        from neural_monitor import NeuralMonitor
        from defense_coordinator import DefenseCoordinator
        from azure_storage_defense import AzureStorageDefense

        print("✅ All modules imported successfully")

        # Test initialization
        print("\n🔧 Testing system initialization...")

        anomaly_detector = AnomalyDetector()
        print(f"✅ Anomaly Detector: {anomaly_detector.status}")

        threat_analyzer = ThreatAnalyzer()
        print(f"✅ Threat Analyzer: {threat_analyzer.status}")

        neural_monitor = NeuralMonitor()
        print(f"✅ Neural Monitor: {neural_monitor.status}")

        defense_coordinator = DefenseCoordinator()
        print(f"✅ Defense Coordinator: {defense_coordinator.status}")

        azure_defense = AzureStorageDefense()
        print(f"✅ Azure Storage Defense: {azure_defense.status}")

        # Test basic functionality
        print("\n⚡ Testing basic functionality...")

        # Test anomaly detection
        anomalies = await anomaly_detector.scan_for_anomalies()
        print(f"✅ Anomaly scan completed: {len(anomalies)} anomalies detected")

        # Test threat analysis
        threats = await threat_analyzer.analyze_recent_activity()
        print(f"✅ Threat analysis completed: {len(threats)} threats detected")

        # Test neural monitoring
        neural_status = await neural_monitor.get_status()
        print(f"✅ Neural status retrieved: {neural_status.get('current_version', 'unknown')}")

        # Test defense coordination
        defense_status = await defense_coordinator.get_defense_status()
        print(f"✅ Defense status retrieved: {defense_status.get('coordinator_status', 'unknown')}")

        # Test Azure storage (mock mode)
        storage_status = await azure_defense.get_storage_status()
        print(f"✅ Storage status retrieved: {storage_status.get('status', 'unknown')}")

        print("\n🎉 All AI Defense systems tested successfully!")
        print(f"🕒 Test completed at: {datetime.utcnow().isoformat()}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_defense_systems())
    sys.exit(0 if success else 1)