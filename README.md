# 🚀 MCP Quickstart: Custom Client & Server with LLM Integration

This project provides a quick and practical starting point to understand and experiment with the **Model Context Protocol (MCP)** by implementing both a custom **MCP server** and **MCP client**, along with integration to a **Large Language Model (LLaMA 4)** via **Groq API**.

## 💡 What This Project Does

* **MCP Server (`servers/`)**

  * Exposes 3 tools via MCP protocol:

    * `get_weather`: Get weather for a specified city.
    * `get_gold_price`: Get the current gold price.
    * `get_bitcoin_price`: Get the latest Bitcoin price.

* **MCP Client (`clients/`)**

  * Connects to the MCP server.
  * Retrieves the list of tools available.
  * Passes tools to a connected LLM (LLaMA 4 via Groq API).
  * Allows the LLM to invoke tools based on user prompts.

* **LLM Interface**

  * Communicates with the Groq LLM API.
  * Provides tool definitions as context so the LLM can call them when needed.

> 🔑 **Groq API Key**: Get your API key from [https://console.groq.com/keys](https://console.groq.com/keys) to enable LLM integration.


## 📁 Project Structure

```
mcp-quickstart/
├── clients/         # MCP client implementation
├── servers/         # MCP server with tool definitions
├── utils/           # Shared helpers
├── main.py          # Start point: runs client-server 
├── requirements.txt # Dependency list for pip users
├── pyproject.toml   # For uv-based dependency management
└── README.md
```

## ⚙️ How to Run

### Option 1: Using `pip`

```bash
# Clone the repo
git clone https://github.com/somnathsingh31/mcp-quickstart.git
cd mcp-quickstart

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the project
python main.py
```

### Option 2: Using [`uv`](https://github.com/astral-sh/uv)

```bash
# Clone the repo
git clone https://github.com/somnathsingh31/mcp-quickstart.git
cd mcp-quickstart

# Install uv if not installed
curl -Ls https://astral.sh/uv/install.sh | bash

# Sync environment and install dependencies
uv sync

# Run the project
uv run main.py
```

This will start the MCP client, connect to the custom MCP server, fetch tool definitions, and pass them to the LLM for dynamic invocation based on user queries.

## 🧠 Key Concepts Demonstrated

* Custom implementation of the MCP protocol
* Dynamic tool selection and execution by LLM
* Tool call architecture using JSON-based schemas
* End-to-end integration with Groq's hosted LLaMA 4

## 📚 References

* [MCP Protocol](https://modelcontextprotocol.io/)
* [Groq](https://console.groq.com/)

## 📝 License

Licensed under the [MIT License](LICENSE).
