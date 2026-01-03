#!/usr/bin/env python3
"""
Test Container creation functionality
"""
import os
import sys

def test_create_container():
    """Test creating Container"""
    
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
        
        print("🎉 Test creating new Container")
        print("=" * 60)
        
        # Get nodes and find an online one
        nodes = api.nodes.get()
        node = None
        for n in nodes:
            if n['status'] == 'online':
                node = n['node']
                print(f"✅ Using online node: {node}")
                break
        
        if not node:
            print("❌ No online nodes found.")
            return False

        # Try to find a template
        template = None
        storage_list = api.nodes(node).storage.get()
        for s in storage_list:
            if "vztmpl" in s.get("content", ""):
                storage = s["storage"]
                try:
                    volumes = api.nodes(node).storage(storage).content.get(content="vztmpl")
                    if volumes:
                        template = volumes[0]["volid"]
                        print(f"✅ Found template: {template}")
                        break
                except:
                    continue
        
        if not template:
            print("❌ No container template found. Cannot proceed with creation test.")
            return False

        # Find an available CT ID
        vmid = "900"
        while True:
            try:
                api.nodes(node).lxc(vmid).config.get()
                vmid = str(int(vmid) + 1)
            except:
                print(f"✅ Container ID {vmid} is available")
                break
        
        # Create Container
        print(f"Attempting to create container {vmid} with template {template}")
        
        result = ct_tools.create_container(
            node=node,
            vmid=vmid,
            name="test-ct-demo",
            ostemplate=template,
            cpus=1,
            memory=512,
            disk_size=4,
            password="password123"
        )
        
        for content in result:
            print(content.text)
            
        return True
        
    except Exception as e:
        print(f"❌ Creation failed: {e}")
        return False

if __name__ == "__main__":
    test_create_container()
