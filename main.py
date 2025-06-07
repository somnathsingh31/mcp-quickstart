import asyncio
from pathlib import Path
from clients.client import start_chat
if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    server_script_path = f"{current_dir}/servers/server.py"
    asyncio.run(start_chat(server_script_path))