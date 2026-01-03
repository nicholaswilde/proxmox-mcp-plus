# Proxmox MCP Plus

## Project Overview
**Proxmox MCP Plus** is an enhanced Python-based Model Context Protocol (MCP) server for interacting with Proxmox virtualization platforms. It allows LLMs (like Claude, Gemini) and other MCP clients to manage Proxmox resources directly.

**Key Features:**
*   **VM Lifecycle Management:** Create, start, stop, shutdown, reset, and delete VMs.
*   **Container Support:** Manage LXC containers (list, start, stop, restart, update resources).
*   **Monitoring:** View nodes, VMs, storage, and cluster status.
*   **OpenAPI Integration:** Can be exposed as standard REST endpoints via `mcpo`.
*   **Open WebUI Integration:** Designed to work with Open WebUI.

## Building and Running

### Prerequisites
*   Python 3.9+
*   `uv` package manager (recommended)
*   Access to a Proxmox server (Hostname, API Token)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd proxmox-mcp-plus
    ```
2.  **Set up virtual environment:**
    ```bash
    uv venv
    source .venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    uv pip install -e ".[dev]"
    ```

### Configuration
1.  Create the configuration directory and file:
    ```bash
    mkdir -p proxmox-config
    cp proxmox-config/config.example.json proxmox-config/config.json
    ```
2.  Edit `proxmox-config/config.json` with your Proxmox credentials.

### Running the Server

**Standard MCP Server:**
```bash
./start_server.sh
# Or manually:
export PROXMOX_MCP_CONFIG="proxmox-config/config.json"
python -m proxmox_mcp.server
```

**OpenAPI / REST Server:**
```bash
./start_openapi.sh
```
This exposes the server on port 8811 (default).

**Docker:**
```bash
docker build -t proxmox-mcp-api .
docker run -d -p 8811:8811 -v $(pwd)/proxmox-config:/app/proxmox-config proxmox-mcp-api
```

## Development Conventions

### Project Structure
*   `src/proxmox_mcp/`: Main source code.
    *   `server.py`: Entry point and MCP server definition.
    *   `tools/`: Implementation of specific tools (VM, Node, Storage, etc.).
    *   `config/`: Configuration loading and validation.
    *   `core/`: Core logic (Proxmox connection).
*   `tests/`: Unit tests (run with `pytest`).
*   `test_scripts/`: Integration test scripts.

### Coding Style
*   **Formatting:** The project likely uses `black` (listed in `dev` dependencies).
*   **Linting:** The project uses `ruff` (listed in `dev` dependencies).
*   **Type Checking:** `mypy` is used for static type checking.

### Testing
*   **Unit Tests:** Run `pytest` from the root directory.
*   **Integration Tests:** Run scripts in `test_scripts/` (e.g., `python test_scripts/test_vm_power.py`). These require a configured and accessible Proxmox server.

### Dependencies
Managed via `pyproject.toml`. Key libraries include:
*   `mcp`: Model Context Protocol SDK.
*   `proxmoxer`: Python wrapper for Proxmox API.
*   `pydantic`: Data validation.
*   `fastapi` / `uvicorn`: For the HTTP server component.
