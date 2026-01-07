"""
Azure Storage Defense Module for AI Defense Container
Provides Azure Storage integration for repository protection.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
import json
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)

class AzureStorageDefense:
    """Azure Storage integration for repository defense"""

    def __init__(self):
        self.status = "initializing"
        self.blob_service_client = None
        self.container_name = "ai-defense-data"
        self.backup_container = "ai-defense-backups"
        self.threat_data = []
        self.defense_metrics = {}

        # Initialize Azure Storage connection
        self._initialize_azure_storage()

        self.status = "ready"
        logger.info("Azure Storage defense initialized")

    def _initialize_azure_storage(self):
        """Initialize Azure Storage connection"""
        try:
            connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
            if not connection_string:
                logger.warning("Azure Storage connection string not found, using mock mode")
                self.blob_service_client = None
                return

            self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            # Ensure containers exist
            self._ensure_containers()

        except Exception as e:
            logger.error(f"Failed to initialize Azure Storage: {e}")
            self.blob_service_client = None

    def _ensure_containers(self):
        """Ensure required containers exist"""
        if not self.blob_service_client:
            return

        try:
            # Create main container
            self.blob_service_client.create_container(self.container_name, public_access=None)
            # Create backup container
            self.blob_service_client.create_container(self.backup_container, public_access=None)
            logger.info("Azure Storage containers verified/created")
        except AzureError as e:
            if "ContainerAlreadyExists" not in str(e):
                logger.error(f"Failed to create containers: {e}")

    async def store_threat_data(self, threat_data: Dict[str, Any]) -> bool:
        """Store threat detection data in Azure Storage"""
        try:
            if not self.blob_service_client:
                # Mock storage for development
                self.threat_data.append(threat_data)
                logger.info("Stored threat data (mock mode)")
                return True

            # Generate blob name
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            threat_id = threat_data.get("id", "unknown")
            blob_name = f"threats/{timestamp}_{threat_id}.json"

            # Convert to JSON
            data_json = json.dumps(threat_data, indent=2, default=str)

            # Upload to blob storage
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            blob_client.upload_blob(data_json, overwrite=True)

            logger.info(f"Stored threat data: {blob_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to store threat data: {e}")
            return False

    async def retrieve_threat_data(self, threat_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve threat data from Azure Storage"""
        try:
            if not self.blob_service_client:
                # Return mock data
                return [t for t in self.threat_data if t.get("id") == threat_id]

            # List blobs in threats directory
            container_client = self.blob_service_client.get_container_client(self.container_name)
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            threats = []
            blob_list = container_client.list_blobs(name_starts_with="threats/")

            for blob in blob_list:
                try:
                    # Check if blob is recent enough
                    blob_date = datetime.fromisoformat(blob.last_modified.isoformat())
                    if blob_date < cutoff_date:
                        continue

                    # Check if blob matches threat_id
                    if threat_id in blob.name:
                        blob_client = container_client.get_blob_client(blob.name)
                        data = blob_client.download_blob().readall()
                        threat_data = json.loads(data)
                        threats.append(threat_data)

                except Exception as e:
                    logger.error(f"Error processing blob {blob.name}: {e}")
                    continue

            return threats

        except Exception as e:
            logger.error(f"Failed to retrieve threat data: {e}")
            return []

    async def backup_defense_models(self, model_data: Dict[str, Any]) -> bool:
        """Backup AI defense models to Azure Storage"""
        try:
            if not self.blob_service_client:
                logger.info("Model backup skipped (mock mode)")
                return True

            # Generate backup blob name
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            model_name = model_data.get("name", "unknown")
            blob_name = f"models/{timestamp}_{model_name}_backup.json"

            # Convert to JSON
            data_json = json.dumps(model_data, indent=2, default=str)

            # Upload to backup container
            blob_client = self.blob_service_client.get_blob_client(
                container=self.backup_container,
                blob=blob_name
            )

            blob_client.upload_blob(data_json, overwrite=True)

            logger.info(f"Backed up model: {blob_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to backup model: {e}")
            return False

    async def restore_defense_models(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Restore AI defense models from Azure Storage"""
        try:
            if not self.blob_service_client:
                logger.warning("Model restore not available (mock mode)")
                return None

            # Find latest backup for model
            container_client = self.blob_service_client.get_container_client(self.backup_container)
            blob_list = list(container_client.list_blobs(name_starts_with=f"models/"))

            # Filter for model name and sort by date
            model_blobs = [b for b in blob_list if model_name in b.name]
            if not model_blobs:
                logger.warning(f"No backups found for model: {model_name}")
                return None

            # Get latest backup
            latest_blob = max(model_blobs, key=lambda b: b.last_modified)

            # Download and parse
            blob_client = container_client.get_blob_client(latest_blob.name)
            data = blob_client.download_blob().readall()
            model_data = json.loads(data)

            logger.info(f"Restored model from: {latest_blob.name}")
            return model_data

        except Exception as e:
            logger.error(f"Failed to restore model {model_name}: {e}")
            return None

    async def store_defense_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Store defense performance metrics"""
        try:
            if not self.blob_service_client:
                # Store in memory for mock mode
                self.defense_metrics.update(metrics)
                logger.info("Stored defense metrics (mock mode)")
                return True

            # Generate metrics blob name
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            blob_name = f"metrics/{timestamp}_defense_metrics.json"

            # Add timestamp
            metrics["stored_at"] = datetime.utcnow().isoformat()

            # Convert to JSON
            data_json = json.dumps(metrics, indent=2, default=str)

            # Upload to blob storage
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            blob_client.upload_blob(data_json, overwrite=True)

            logger.info(f"Stored defense metrics: {blob_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to store defense metrics: {e}")
            return False

    async def get_defense_metrics_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """Retrieve defense metrics history"""
        try:
            if not self.blob_service_client:
                # Return mock metrics
                return [self.defense_metrics] if self.defense_metrics else []

            # List metrics blobs
            container_client = self.blob_service_client.get_container_client(self.container_name)
            cutoff_date = datetime.utcnow() - timedelta(days=days)

            metrics_history = []
            blob_list = container_client.list_blobs(name_starts_with="metrics/")

            for blob in blob_list:
                try:
                    # Check if blob is recent enough
                    blob_date = datetime.fromisoformat(blob.last_modified.isoformat())
                    if blob_date < cutoff_date:
                        continue

                    blob_client = container_client.get_blob_client(blob.name)
                    data = blob_client.download_blob().readall()
                    metrics = json.loads(data)
                    metrics_history.append(metrics)

                except Exception as e:
                    logger.error(f"Error processing metrics blob {blob.name}: {e}")
                    continue

            # Sort by timestamp
            metrics_history.sort(key=lambda x: x.get("stored_at", ""), reverse=True)

            return metrics_history

        except Exception as e:
            logger.error(f"Failed to retrieve metrics history: {e}")
            return []

    async def quarantine_suspicious_data(self, data_id: str, data: Dict[str, Any]) -> bool:
        """Quarantine suspicious data for analysis"""
        try:
            if not self.blob_service_client:
                logger.info(f"Quarantined data {data_id} (mock mode)")
                return True

            # Generate quarantine blob name
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            blob_name = f"quarantine/{timestamp}_{data_id}.json"

            # Add quarantine metadata
            quarantine_data = {
                "original_data": data,
                "quarantined_at": datetime.utcnow().isoformat(),
                "data_id": data_id,
                "status": "quarantined"
            }

            # Convert to JSON
            data_json = json.dumps(quarantine_data, indent=2, default=str)

            # Upload to quarantine area
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )

            blob_client.upload_blob(data_json, overwrite=True)

            logger.info(f"Quarantined suspicious data: {data_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to quarantine data {data_id}: {e}")
            return False

    async def get_quarantine_status(self) -> Dict[str, Any]:
        """Get status of quarantined data"""
        try:
            if not self.blob_service_client:
                return {"quarantined_items": 0, "total_size": 0}

            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_list = list(container_client.list_blobs(name_starts_with="quarantine/"))

            total_size = sum(blob.size for blob in blob_list)

            return {
                "quarantined_items": len(blob_list),
                "total_size": total_size,
                "last_updated": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get quarantine status: {e}")
            return {"error": str(e)}

    async def cleanup_old_data(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """Clean up old threat data and metrics"""
        try:
            if not self.blob_service_client:
                logger.info("Cleanup skipped (mock mode)")
                return {"cleaned_items": 0}

            container_client = self.blob_service_client.get_container_client(self.container_name)
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

            cleaned_count = 0
            blob_list = list(container_client.list_blobs())

            for blob in blob_list:
                try:
                    blob_date = datetime.fromisoformat(blob.last_modified.isoformat())
                    if blob_date < cutoff_date:
                        # Delete old blob
                        blob_client = container_client.get_blob_client(blob.name)
                        blob_client.delete_blob()
                        cleaned_count += 1

                except Exception as e:
                    logger.error(f"Error cleaning blob {blob.name}: {e}")
                    continue

            logger.info(f"Cleaned up {cleaned_count} old items")
            return {"cleaned_items": cleaned_count}

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return {"error": str(e)}

    async def get_storage_status(self) -> Dict[str, Any]:
        """Get Azure Storage status and usage"""
        try:
            if not self.blob_service_client:
                return {
                    "status": "mock_mode",
                    "containers": ["ai-defense-data", "ai-defense-backups"],
                    "total_blobs": len(self.threat_data)
                }

            # Get container properties
            main_container = self.blob_service_client.get_container_client(self.container_name)
            backup_container = self.blob_service_client.get_container_client(self.backup_container)

            main_blobs = list(main_container.list_blobs())
            backup_blobs = list(backup_container.list_blobs())

            return {
                "status": "connected",
                "containers": [self.container_name, self.backup_container],
                "main_container_blobs": len(main_blobs),
                "backup_container_blobs": len(backup_blobs),
                "total_size_mb": (sum(b.size for b in main_blobs) + sum(b.size for b in backup_blobs)) / (1024 * 1024),
                "last_checked": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get storage status: {e}")
            return {"error": str(e)}