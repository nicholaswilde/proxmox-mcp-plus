#!/usr/bin/env python3
"""
Test Container deletion functionality
"""
import os
import sys

def test_delete_container():
    """Test deleting Container"""
    
    # Set configuration
    if 'PROXMOX_MCP_CONFIG' not in os.environ:
        os.environ['PROXMOX_MCP_CONFIG'] = 'proxmox-config/config.json'
    
    try:
        from proxmox_mcp.config.loader import load_config
        from proxmox_mcp.core.proxmox import ProxmoxManager
        from proxmox_mcp.tools.containers import ContainerTools
        
        config = load_config(os.environ['PROXMOX_MCP_CONFIG'])
        manager = ProxmoxManager(config.proxmox, config.auth)
        api = manager.get_api()
        
        ct_tools = ContainerTools(api)
        
        print("🎉 Test deleting Container")
        print("=" * 60)
        
        node = "pve01" # Hardcoded based on creation test output
        vmid = "900"
        
        print(f"Attempting to delete container {vmid} on node {node}")
        
        result = ct_tools.delete_container(
            node=node,
            vmid=vmid,
            force=True
        )
        
        for content in result:
            print(content.text)
            
        return True
        
    except Exception as e:
        print(f"❌ Deletion failed: {e}")
        return False

if __name__ == "__main__":
    test_delete_container()
