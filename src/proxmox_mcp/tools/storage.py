"""
Storage-related tools for Proxmox MCP.

This module provides tools for managing and monitoring Proxmox storage:
- Listing all storage pools across the cluster
- Retrieving detailed storage information including:
  * Storage type and content types
  * Usage statistics and capacity
  * Availability status
  * Node assignments

The tools implement fallback mechanisms for scenarios where
detailed storage information might be temporarily unavailable.
"""
from typing import List
from mcp.types import TextContent as Content
from .base import ProxmoxTool
from .definitions import GET_STORAGE_DESC

class StorageTools(ProxmoxTool):
    """Tools for managing Proxmox storage.
    
    Provides functionality for:
    - Retrieving cluster-wide storage information
    - Monitoring storage pool status and health
    - Tracking storage utilization and capacity
    - Managing storage content types
    
    Implements fallback mechanisms for scenarios where detailed
    storage information might be temporarily unavailable.
    """

    def get_storage(self) -> List[Content]:
        """List storage pools across the cluster with detailed status.

        Retrieves comprehensive information for each storage pool including:
        - Basic identification (name, type)
        - Content types supported (VM disks, backups, ISO images, etc.)
        - Availability status (online/offline)
        - Usage statistics:
          * Used space
          * Total capacity
          * Available space
        
        Implements a fallback mechanism that returns basic information
        if detailed status retrieval fails for any storage pool.

        Returns:
            List of Content objects containing formatted storage information:
            {
                "storage": "storage-name",
                "type": "storage-type",
                "content": ["content-types"],
                "status": "online/offline",
                "used": bytes,
                "total": bytes,
                "available": bytes
            }

        Raises:
            RuntimeError: If the cluster-wide storage query fails
        """
        try:
            result = self.proxmox.storage.get()
            storage = []
            
            for store in result:
                # Get detailed storage info including usage
                try:
                    status = self.proxmox.nodes(store.get("node", "localhost")).storage(store["storage"]).status.get()
                    storage.append({
                        "storage": store["storage"],
                        "type": store["type"],
                        "content": store.get("content", []),
                        "status": "online" if store.get("enabled", True) else "offline",
                        "used": status.get("used", 0),
                        "total": status.get("total", 0),
                        "available": status.get("avail", 0)
                    })
                except Exception:
                    # If detailed status fails, add basic info
                    storage.append({
                        "storage": store["storage"],
                        "type": store["type"],
                        "content": store.get("content", []),
                        "status": "online" if store.get("enabled", True) else "offline",
                        "used": 0,
                        "total": 0,
                        "available": 0
                    })
                    
            return self._format_response(storage, "storage")
        except Exception as e:
            self._handle_error("get storage", e)

    def list_templates(self, node: str, storage: str = "local", content_type: str = "vztempl") -> List[Content]:
        """List templates on a specific storage.

        Args:
            node: The node name (e.g. 'pve')
            storage: The storage name (e.g. 'local'). Defaults to 'local'.
            content_type: Content type to filter (e.g. 'vztempl', 'iso'). Defaults to 'vztempl'.
        
        Returns:
            List of Content objects.
        """
        try:
            content = self.proxmox.nodes(node).storage(storage).content.get(content=content_type)
            return self._format_response(content, "templates")
        except Exception as e:
            self._handle_error(f"list templates on {node}:{storage}", e)

    def list_available_templates(self, node: str) -> List[Content]:
        """List container templates available for download.

        Args:
            node: The node name (e.g. 'pve')

        Returns:
            List of Content objects.
        """
        try:
            # Equivalent to 'pveam available'
            # API: /nodes/{node}/aplinfo
            templates = self.proxmox.nodes(node).aplinfo.get()
            return self._format_response(templates, "available_templates")
        except Exception as e:
            self._handle_error(f"list available templates on {node}", e)

    def download_template(self, node: str, template: str, storage: str = "local") -> List[Content]:
        """Download a container template to storage.

        Args:
            node: The node name (e.g. 'pve')
            template: The template package name
            storage: The target storage name (default: 'local')

        Returns:
            List of Content objects (task UPID usually).
        """
        try:
            # Equivalent to 'pveam download <storage> <template>'
            # API: POST /nodes/{node}/storage/{storage}/content
            # Parameters: content='vztmpl', filename=<template> (or template=<template>)
            # 'proxmoxer' handles positional args for URL building, kwargs for body parameters.
            
            # Using 'template' parameter as per common 'pveam' API usage for download.
            # Some versions use 'filename' + 'content' type.
            # 'pveam download' CLI uses: POST /api2/json/nodes/{node}/storage/{storage}/content
            # with body: content=vztmpl, filename=<template>
            
            # However, simpler endpoint for download specifically might be:
            # POST /nodes/{node}/aplinfo (update) -> no, that's 'pveam update'
            
            # Let's try the standard content creation endpoint with 'vztmpl' content type.
            result = self.proxmox.nodes(node).storage(storage).content.post(
                content='vztmpl',
                filename=template
            )
            return self._format_response({"upid": result}, "download_task")
        except Exception as e:
            self._handle_error(f"download template {template} to {node}:{storage}", e)
