# Microsoft Copilot Agent SDK for Python

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.8--3.12-blue.svg)](https://www.python.org/)
[![Maintained](https://img.shields.io/badge/Maintained-yes-green.svg)](https://github.com/aihq-labs/copilot-demo)

A Python SDK for interacting with Microsoft Copilot Studio agents. This SDK provides a simple, high-level interface for building applications that communicate with your Copilot agents.

**Developed by [AIHQ.ie](https://www.aihq.ie)**

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Authentication](#authentication)
- [CLI Reference](#cli-reference)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Easy Configuration**: Environment variable-based configuration (.env file)
- **Multiple Auth Methods**: Support for no authentication, interactive (device code), client credentials, and default Azure credential chain
- **No Auth Support**: Works with publicly accessible agents (no Azure AD required)
- **Context Management**: Maintain conversation context across multiple messages
- **CLI Interface**: Ready-to-use command-line interface for testing and interaction
- **Async Support**: Built on async/await for efficient I/O operations
- **Type-Safe**: Fully typed with dataclasses for configuration management

## Prerequisites

- **Python 3.12.x** (recommended) or Python 3.8-3.11
- Microsoft Copilot Studio agent metadata
- Azure AD application registration (only required if using authenticated agents)

### Python Version Notes
- **Recommended**: Python 3.12.x for best performance and latest features
- **Minimum**: Python 3.8
- **Maximum**: Python 3.12.x (Python 3.13+ not yet supported by Microsoft Agents SDK)
- **Tested on**: Python 3.12, 3.11, 3.10, 3.9, 3.8

> **Important**: The Microsoft Agents SDK packages currently require Python <3.13. When Python 3.13 support is added by Microsoft, this SDK will be updated accordingly.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/aihq-labs/copilot-demo.git
cd copilot-demo
```

2. Ensure you have Python 3.12 installed:
```bash
# Check your Python version
python --version
# Should show: Python 3.12.x (3.8-3.12 supported, 3.12 recommended)

# Or use python3 if python points to Python 2
python3 --version
```

3. Create a virtual environment:
```bash
# Using Python 3.12
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate

# Verify virtual environment Python version
python --version
```

4. Upgrade pip:
```bash
python -m pip install --upgrade pip
```

5. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure your agent by creating a `.env` file:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and add your agent configuration:
   - `COPILOT_STUDIO_AGENT_ENVIRONMENT_ID` - Your agent environment ID
   - `COPILOT_STUDIO_AGENT_TENANT_ID` - Your Azure AD tenant ID
   - `COPILOT_STUDIO_AGENT_APP_ID` - Your agent app ID
   - `COPILOT_STUDIO_AGENT_AGENT_IDENTIFIER` - Your agent schema name
   - `COPILOT_STUDIO_AGENT_AUTH_MODE` - Authentication mode (e.g., "interactive", "client_credentials", "none")
   - `COPILOT_STUDIO_AGENT_APP_CLIENT_ID` - Azure AD Client ID (if using authentication)

## Quick Start

### Using the CLI

#### Interactive Chat Mode
```bash
python cli.py
```

This starts an interactive chat session where you can:
- Type messages and get responses
- Use `reset` to clear conversation context
- Use `exit`, `quit`, or `bye` to end the session

#### Send a Single Message
```bash
python cli.py --message "What is the weather today?"
```

#### Send Multiple Messages
```bash
python cli.py --message "Hello" --message "Tell me a joke"
```

#### View Configuration
```bash
python cli.py --config
```

### Using the SDK Programmatically

#### Simple Example
```python
from copilot_sdk import CopilotAgentClient

# Initialize the client
client = CopilotAgentClient()

# Send a message
response = client.send_message("Hello, how are you?")
print(response)

# Send another message (context is maintained)
response = client.send_message("Tell me more about that")
print(response)

# Reset context
client.reset_context()
```

#### Interactive Chat Loop
```python
from copilot_sdk import CopilotAgentClient

# Initialize and start chat
client = CopilotAgentClient()
client.chat_loop()  # Starts interactive chat
```

#### Async Usage
```python
import asyncio
from copilot_sdk import CopilotAgentClient

async def main():
    client = CopilotAgentClient()

    # Send messages asynchronously
    response = await client.send_message_async("Hello!")
    print(response)

    # Send multiple messages
    messages = ["What is AI?", "How does it work?"]
    responses = await client.send_messages_async(messages)
    for msg, resp in zip(messages, responses):
        print(f"Q: {msg}\nA: {resp}\n")

asyncio.run(main())
```

#### Custom Configuration
```python
from copilot_sdk import CopilotAgentClient, CopilotConfig

# Load configuration (reads from .env by default)
config = CopilotConfig()
client = CopilotAgentClient(config=config)

# Display configuration
config.display()

# Get configuration info
info = client.get_config_info()
print(info)
```

## Configuration

### .env File (Primary Configuration)

The SDK uses environment variables from a `.env` file for all configuration. This keeps sensitive values out of version control.

**Required Variables:**
```bash
# Agent Configuration
COPILOT_STUDIO_AGENT_ENVIRONMENT_ID=your-environment-id
COPILOT_STUDIO_AGENT_TENANT_ID=your-tenant-id
COPILOT_STUDIO_AGENT_APP_ID=your-app-id
COPILOT_STUDIO_AGENT_AGENT_IDENTIFIER=your-schema-name

# Authentication
COPILOT_STUDIO_AGENT_AUTH_MODE=interactive  # Options: "none", "interactive", "client_credentials", "directline"
COPILOT_STUDIO_AGENT_APP_CLIENT_ID=your-client-id  # Required if auth mode is not "none"
```

**Optional Variables:**
```bash
# Agent Display
COPILOT_STUDIO_AGENT_NAME=Copilot Agent
COPILOT_STUDIO_AGENT_INSTRUCTIONS=You are a helpful AI assistant.

# API Settings
COPILOT_STUDIO_API_BASE_URL=https://api.copilotstudio.microsoft.com
COPILOT_STUDIO_API_TIMEOUT=30
COPILOT_STUDIO_API_MAX_RETRIES=3
POWER_PLATFORM_CLOUD=PROD

# Azure Credentials (for client_credentials mode)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_SECRET=your-client-secret

# DirectLine (for directline auth mode)
COPILOT_STUDIO_WEB_CHANNEL_SECURITY_KEY=your-directline-secret
```

**Setup:**
1. Copy the example file: `cp .env.example .env`
2. Edit `.env` and fill in your values
3. The `.env` file is gitignored and won't be committed

> **Note**: `config.yaml` is optional and only used as a fallback. All configuration should be in `.env` for security.

## Authentication

The SDK supports multiple authentication modes to accommodate different agent security configurations.

### No Authentication Mode (Recommended for Testing)

For agents configured with "No Auth" security in Copilot Studio:

1. Set auth mode in `.env`:
```bash
COPILOT_STUDIO_AGENT_AUTH_MODE=none
```

2. No Azure AD Client ID required!

3. Example usage:
```python
from copilot_sdk import CopilotAgentClient

# Works immediately without any authentication setup
client = CopilotAgentClient()
response = client.send_message("Hello!")
print(response)
```

**When to use**:
- Testing and development
- Publicly accessible agents
- Agents that don't require user identity
- Quick prototyping

**Note**: Agents with "No Auth" can be accessed by anyone with the endpoint URL. Use authenticated modes for production scenarios requiring user identity or access control.

### Interactive Mode

Uses Azure Device Code Flow for authentication:

1. Run the CLI or SDK
2. You'll be prompted to visit a URL
3. Enter the provided code
4. Complete authentication in your browser

### Client Credentials Mode

For non-interactive scenarios (e.g., services, automation):

1. Set auth mode in `.env`:
```bash
COPILOT_STUDIO_AGENT_AUTH_MODE=client_credentials
COPILOT_STUDIO_AGENT_APP_CLIENT_ID=your-client-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_SECRET=your-client-secret
```

### Default Azure Credential Chain

Uses Azure's default credential chain (environment, managed identity, CLI, etc.):

Set in `.env`:
```bash
COPILOT_STUDIO_AGENT_AUTH_MODE=default
```

## Azure AD Setup

**Note**: Only required if using authenticated modes (not "none")

Your Azure AD application needs:

1. **App Registration**:
   - Create an app registration in Azure AD
   - Note the Client ID

2. **API Permissions**:
   - Add delegated permission: `CopilotStudio.Copilots.Invoke`
   - Grant admin consent if required

3. **Authentication**:
   - For interactive mode: Enable "Mobile and desktop applications" platform
   - For client credentials: Create a client secret

4. **Set Environment Variable**:
```bash
export COPILOT_STUDIO_AGENT_APP_CLIENT_ID="your-client-id"
```

## CLI Reference

```bash
# Interactive chat (default)
python cli.py

# Send single message
python cli.py -m "Your message"
python cli.py --message "Your message"

# Send multiple messages
python cli.py -m "Message 1" -m "Message 2"

# Disable context between messages
python cli.py -m "Message" --no-context

# Show configuration
python cli.py --config

# Use custom config file (optional - .env is primary)
python cli.py --config-file /path/to/config.yaml

# Verbose output
python cli.py -v

# Show help
python cli.py --help
```

## SDK Architecture

```
copilot-demo/
├── copilot_sdk/           # Core SDK package
│   ├── __init__.py        # Package exports
│   ├── client.py          # Main client class
│   ├── config.py          # Configuration management
│   └── auth.py            # Authentication handling
├── cli.py                 # Command-line interface
├── api.py                 # FastAPI REST API server
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment variable template
├── config.yaml.example    # Optional config.yaml template
├── requirements.txt       # Python dependencies
├── LICENSE                # Apache 2.0 License
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## API Reference

### CopilotAgentClient

Main client class for interacting with agents.

#### Methods

- `send_message(message: str, maintain_context: bool = True) -> str`
  - Send a message and get response (synchronous)

- `send_message_async(message: str, maintain_context: bool = True) -> str`
  - Send a message and get response (asynchronous)

- `send_messages(messages: List[str]) -> List[str]`
  - Send multiple messages (synchronous)

- `send_messages_async(messages: List[str]) -> List[str]`
  - Send multiple messages (asynchronous)

- `reset_context()`
  - Clear conversation context

- `chat_loop()`
  - Start interactive chat (synchronous)

- `chat_loop_async()`
  - Start interactive chat (asynchronous)

- `get_config_info() -> Dict[str, Any]`
  - Get current configuration information

### CopilotConfig

Configuration management class.

#### Methods

- `validate() -> bool`
  - Validate configuration

- `display()`
  - Display configuration (with masked sensitive data)

## Troubleshooting

### Authentication Errors

**Problem**: "Missing client_id" error for authenticated agents

**Solution**:
1. If your agent has "No Auth" security, set in `.env`:
   ```bash
   COPILOT_STUDIO_AGENT_AUTH_MODE=none
   ```
2. If your agent requires authentication, set in `.env`:
   ```bash
   COPILOT_STUDIO_AGENT_AUTH_MODE=interactive
   COPILOT_STUDIO_AGENT_APP_CLIENT_ID=your-client-id
   ```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'semantic_kernel'`

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration Errors

**Problem**: "Configuration validation failed"

**Solution**:
1. Check that `.env` file exists: `cp .env.example .env`
2. Verify all required environment variables are set in `.env`
3. Run `python cli.py --config` to see current configuration
4. Ensure `.env` file is in the same directory as your script

### Agent Connection Errors

**Problem**: Cannot connect to agent

**Solution**:
1. Verify your agent metadata in `.env` file (environment_id, tenant_id, app_id, schema_name)
2. Check Azure AD permissions
3. Ensure your Azure AD app has the required API permissions
4. Try re-authenticating by removing cached credentials (delete `.token_cache.json`)

## Examples

### Example 1: Simple Q&A Bot
```python
from copilot_sdk import CopilotAgentClient

def answer_questions(questions):
    client = CopilotAgentClient()

    for question in questions:
        print(f"Q: {question}")
        answer = client.send_message(question)
        print(f"A: {answer}\n")

questions = [
    "What is artificial intelligence?",
    "How does machine learning work?",
    "What are neural networks?"
]

answer_questions(questions)
```

### Example 2: Customer Support Bot
```python
from copilot_sdk import CopilotAgentClient

def handle_support_ticket(customer_name, issue):
    client = CopilotAgentClient()

    # Start conversation
    greeting = f"Hello, I'm helping {customer_name} with an issue."
    client.send_message(greeting)

    # Describe issue
    response = client.send_message(f"The customer is experiencing: {issue}")

    return response

# Usage
resolution = handle_support_ticket(
    "John Doe",
    "Unable to log in to their account"
)
print(f"Suggested resolution: {resolution}")
```

### Example 3: Batch Processing
```python
import asyncio
from copilot_sdk import CopilotAgentClient

async def process_batch(items):
    client = CopilotAgentClient()

    tasks = [
        client.send_message_async(f"Process: {item}", maintain_context=False)
        for item in items
    ]

    results = await asyncio.gather(*tasks)
    return results

# Usage
items = ["Item 1", "Item 2", "Item 3"]
results = asyncio.run(process_batch(items))

for item, result in zip(items, results):
    print(f"{item}: {result}")
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Star History

If you find this project useful, please consider giving it a ⭐ on GitHub!

## License

Copyright 2025 AIHQ.ie

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the LICENSE file for the full license text.

## Support

For issues, questions, or contributions, please:
- Open an issue on [GitHub](https://github.com/aihq-labs/copilot-demo/issues)
- Visit [AIHQ.ie](https://www.aihq.ie) for more information
- Check Microsoft Learn documentation for Copilot Studio
- Review Azure AD authentication documentation

## Resources

- [Microsoft Copilot Studio Documentation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/)
- [Microsoft 365 Agents SDK](https://github.com/microsoft/Agents)
- [Semantic Kernel Python](https://learn.microsoft.com/en-us/semantic-kernel/)
- [Azure Identity Python](https://learn.microsoft.com/en-us/python/api/azure-identity/)

## Changelog

### Version 1.0.0 (2025-10-15)
- Initial release
- **Python 3.12 optimized** (supports Python 3.8-3.12)
- Support for no authentication, interactive, and client credentials authentication modes
- CLI interface for testing and interaction
- Full async/await support with Python 3.12 performance improvements
- Conversation context management
- Comprehensive documentation and examples
- Flexible configuration for both public and authenticated agents
- Type hints compatible with Python 3.12 typing system
- **Note**: Python 3.13+ support pending Microsoft Agents SDK update
