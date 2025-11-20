"""
Main client for Microsoft Copilot Studio Agent SDK
Based on official Microsoft Agents SDK - Copilot Studio Client sample
https://github.com/microsoft/Agents/tree/main/samples/python/copilotstudio-client

Copyright 2025 AIHQ.ie
Licensed under the Apache License, Version 2.0
"""

import asyncio
from os import environ
from typing import Optional, List, Dict, Any

from msal import PublicClientApplication, ConfidentialClientApplication, SerializableTokenCache
import os
import aiohttp
import json
from pathlib import Path
from datetime import datetime
import uuid

# Official imports from Microsoft documentation
from microsoft_agents.copilotstudio.client.copilot_client import CopilotClient
from microsoft_agents.copilotstudio.client.connection_settings import ConnectionSettings
from microsoft_agents.copilotstudio.client import AgentType, PowerPlatformCloud

from copilot_sdk.config import CopilotConfig


class CopilotAgentClient:
    """
    Client for interacting with Microsoft Copilot Studio agents

    This directly invokes your specific Copilot Studio agent and gets responses.
    """

    def __init__(self, config: Optional[CopilotConfig] = None, config_path: Optional[str] = None):
        """
        Initialize Copilot Studio Agent Client

        Args:
            config: CopilotConfig object. If None, will be loaded from config_path
            config_path: Path to config.yaml file
        """
        self.config = config or CopilotConfig(config_path)

        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid configuration. Please check config.yaml and environment variables.")

        self._client = None
        self._token = None
        self._initialized = False

        # Token cache file location
        self._token_cache_file = Path.cwd() / ".token_cache.json"

        # Logs directory
        self._logs_dir = Path.cwd() / "logs"
        self._logs_dir.mkdir(exist_ok=True)

        # Current conversation log file
        self._current_log_file = None

    async def _generate_directline_token(self) -> str:
        """Generate DirectLine token from secret"""
        secret = os.getenv("COPILOT_STUDIO_WEB_CHANNEL_SECURITY_KEY")
        if not secret:
            raise ValueError(
                "COPILOT_STUDIO_WEB_CHANNEL_SECURITY_KEY environment variable required for directline mode"
            )

        print("Generating DirectLine token from secret...")

        # DirectLine token generation endpoint
        url = "https://directline.botframework.com/v3/directline/tokens/generate"
        headers = {
            "Authorization": f"Bearer {secret}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    token = data.get("token")
                    expires_in = data.get("expires_in", 1800)
                    print(f"✓ DirectLine token generated (expires in {expires_in}s)\n")
                    return token
                else:
                    error_text = await response.text()
                    raise Exception(f"Failed to generate DirectLine token: {response.status} - {error_text}")

    def _save_token_cache(self, cache: SerializableTokenCache):
        """Save token cache to JSON file"""
        if cache.has_state_changed:
            with open(self._token_cache_file, 'w') as f:
                f.write(cache.serialize())
            print(f"Token cache saved to {self._token_cache_file}")

    def _log_to_file(self, message: str, conversation_id: Optional[str] = None):
        """Log debug message to conversation-specific file"""
        if not conversation_id:
            # Use a temporary log file with UUID
            if not self._current_log_file:
                log_id = str(uuid.uuid4())
                self._current_log_file = self._logs_dir / f"conversation_{log_id}.log"
            log_file = self._current_log_file
        else:
            # Use conversation ID as filename
            log_file = self._logs_dir / f"conversation_{conversation_id}.log"
            self._current_log_file = log_file

        # Append to log file with timestamp
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.utcnow().isoformat()
            f.write(f"[{timestamp}] {message}\n")

    def _log_activity(self, activity, conversation_id: Optional[str] = None):
        """Log full activity details to file"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": getattr(activity, "type", None),
            "text": getattr(activity, "text", None),
            "name": getattr(activity, "name", None),
            "value": str(getattr(activity, "value", None)),
            "channel_data": str(getattr(activity, "channel_data", None)),
            "entities": str(getattr(activity, "entities", None)),
            "label": getattr(activity, "label", None),
            "semantic_action": str(getattr(activity, "semantic_action", None)),
            "id": getattr(activity, "id", None)
        }

        self._log_to_file(f"ACTIVITY: {json.dumps(log_data, indent=2)}", conversation_id)

    def _acquire_token(self) -> str:
        """Acquire authentication token using MSAL with caching"""
        # Check auth mode - DirectLine uses different flow
        if self.config.auth.mode == "directline":
            # DirectLine doesn't use MSAL - uses DirectLine secret
            # Token generation happens in async context, so we'll handle it differently
            return "directline"  # Placeholder, actual token generated in async context

        # MSAL scopes for Copilot Studio
        scopes = ["https://api.powerplatform.com/.default"]

        # Check auth mode
        if self.config.auth.mode == "client_credentials":
            # Use ConfidentialClientApplication for service principal auth
            print("Using client_credentials authentication (no sign-in required)...")

            # Get client secret from environment
            client_secret = os.getenv("AZURE_CLIENT_SECRET")
            if not client_secret:
                raise ValueError(
                    "AZURE_CLIENT_SECRET environment variable required for client_credentials mode"
                )

            app = ConfidentialClientApplication(
                client_id=self.config.auth.client_id,
                client_credential=client_secret,
                authority=f"https://login.microsoftonline.com/{self.config.agent.tenant_id}"
            )

            # Acquire token for client credentials (no user interaction)
            result = app.acquire_token_for_client(scopes=scopes)

            if "access_token" in result:
                print("✓ Authentication successful (service principal)\n")
                return result["access_token"]
            else:
                error_msg = result.get("error_description", result.get("error", "Unknown error"))
                raise Exception(f"Client credentials authentication failed: {error_msg}")

        else:
            # Use PublicClientApplication for interactive auth with persistent cache
            # Create or load token cache from JSON file
            cache = SerializableTokenCache()

            if self._token_cache_file.exists():
                with open(self._token_cache_file, 'r') as f:
                    cache.deserialize(f.read())
                    print(f"✓ Loaded token cache from {self._token_cache_file}")

            app = PublicClientApplication(
                client_id=self.config.auth.client_id,
                authority=f"https://login.microsoftonline.com/{self.config.agent.tenant_id}",
                token_cache=cache
            )

            # Try to get token silently from cache first
            accounts = app.get_accounts()
            result = None

            if accounts:
                print("✓ Found cached account, attempting silent token acquisition...")
                result = app.acquire_token_silent(scopes, account=accounts[0])

                if result and "access_token" in result:
                    print("✓ Using cached token (no sign-in needed)\n")
                    # Save cache
                    self._save_token_cache(cache)
                    return result["access_token"]

            # If no cached token, use interactive authentication
            print("\nInteractive authentication required...")
            print("=" * 60)
            print("A browser window will open for authentication")
            print("Token will be saved for future use")
            print("=" * 60)
            result = app.acquire_token_interactive(scopes)

            if "access_token" in result:
                print(f"✓ Authentication successful! Token saved to {self._token_cache_file}\n")
                # Save the token cache to file
                self._save_token_cache(cache)
                return result["access_token"]
            else:
                error_msg = result.get("error_description", result.get("error", "Unknown error"))
                raise Exception(f"Authentication failed: {error_msg}")

    async def _initialize_client_async(self):
        """Initialize the Copilot Studio client (async)"""
        if self._initialized:
            return

        print(f"\nInitializing Copilot Studio Agent: {self.config.agent.schema_name}")
        print(f"Environment ID: {self.config.agent.environment_id}")
        print(f"Tenant ID: {self.config.agent.tenant_id}\n")

        # Acquire authentication token
        if self.config.auth.mode == "directline":
            # Use DirectLine secret directly (not generated token)
            # CopilotClient accepts the secret as the token
            self._token = os.getenv("COPILOT_STUDIO_WEB_CHANNEL_SECURITY_KEY")
            if not self._token:
                raise ValueError("COPILOT_STUDIO_WEB_CHANNEL_SECURITY_KEY required for directline mode")
            print("✓ Using DirectLine secret for authentication (no sign-in required)\n")
        else:
            # Use MSAL authentication
            self._token = self._acquire_token()

        # Create connection settings with all required parameters
        # Get cloud value from config
        cloud_name = self.config.api.cloud.upper()
        print(f"Using Power Platform Cloud: {cloud_name}")

        # Get the enum value
        try:
            cloud_value = getattr(PowerPlatformCloud, cloud_name)
        except AttributeError:
            # If the specified cloud doesn't exist, list available and use first
            available = [a for a in dir(PowerPlatformCloud) if not a.startswith('_')]
            print(f"Warning: Cloud '{cloud_name}' not found. Available: {', '.join(available)}")
            if available:
                cloud_value = getattr(PowerPlatformCloud, available[0])
                print(f"Using: {available[0]}")
            else:
                raise ValueError(f"No valid PowerPlatformCloud values found")

        settings = ConnectionSettings(
            environment_id=self.config.agent.environment_id,
            agent_identifier=self.config.agent.schema_name,
            cloud=cloud_value,
            copilot_agent_type=AgentType.PUBLISHED,
            custom_power_platform_cloud=None
        )

        # Create Copilot client
        self._client = CopilotClient(settings, self._token)

        self._initialized = True
        print("✓ Agent client initialized successfully!\n")

    def _initialize_client(self):
        """Synchronous wrapper for client initialization"""
        asyncio.run(self._initialize_client_async())

    async def start_conversation_async(self) -> Dict[str, Any]:
        """
        Start a new conversation with the agent

        Returns:
            Dictionary with conversation details
        """
        await self._initialize_client_async()

        print("Starting new conversation...")

        try:
            # start_conversation returns an async generator, iterate over it
            conversation_result = None
            async for result in self._client.start_conversation():
                conversation_result = result
                # Don't break - continue to get all results

            if not conversation_result:
                raise Exception("Failed to start conversation")

            # Extract conversation ID from Activity object
            conversation_id = getattr(conversation_result, "id", None)

            if not conversation_id:
                raise Exception(f"Could not extract conversation ID from result: {conversation_result}")

            # Log conversation start
            self._log_to_file(f"=== CONVERSATION STARTED ===", conversation_id)
            self._log_to_file(f"Conversation ID: {conversation_id}", conversation_id)

            print(f"✓ Conversation started: {conversation_id}")
            print(f"✓ Logging to: logs/conversation_{conversation_id}.log\n")

            return {
                "conversation_id": conversation_id,
                "token": getattr(conversation_result, "token", None),
                "status": "started"
            }

        except Exception as e:
            print(f"Error starting conversation: {e}")
            import traceback
            traceback.print_exc()
            raise

    def start_conversation(self) -> Dict[str, Any]:
        """Synchronous wrapper for start_conversation_async"""
        return asyncio.run(self.start_conversation_async())

    async def send_message_async(self, message: str, conversation_id: Optional[str] = None) -> str:
        """
        Send a message to the agent and get response

        Args:
            message: Message to send
            conversation_id: Optional conversation ID (will start new if not provided)

        Returns:
            Agent's response as a string
        """
        await self._initialize_client_async()

        # Start conversation if no conversation_id provided
        if not conversation_id:
            conv_result = await self.start_conversation_async()
            conversation_id = conv_result["conversation_id"]

        print(f"Sending message: '{message}'...")

        try:
            # Ask question and get response (also an async generator)
            all_responses = []
            thinking_text = []

            # Log the message being sent
            self._log_to_file(f"\n=== USER MESSAGE ===", conversation_id)
            self._log_to_file(f"Message: {message}", conversation_id)

            async for activity in self._client.ask_question(message, conversation_id):
                # Activity is an object, not a dict - use attributes
                activity_type = getattr(activity, "type", None)
                from_info = getattr(activity, "from", None) if hasattr(activity, "from") else None

                # Log full activity details to file instead of printing
                self._log_activity(activity, conversation_id)

                # Get text content
                text = getattr(activity, "text", None)

                # Get role
                role = None
                if from_info:
                    role = getattr(from_info, "role", None)

                # Capture different types of activities
                if activity_type == "typing":
                    # Thinking/typing indicator
                    continue
                elif activity_type == "trace":
                    # Trace activities might contain thinking process
                    if text:
                        thinking_text.append(f"[Thinking] {text}")
                    # Also check name and value
                    name = getattr(activity, "name", None)
                    value = getattr(activity, "value", None)
                    if name:
                        thinking_text.append(f"[Trace: {name}]")
                    if value:
                        thinking_text.append(f"[Trace Data] {value}")
                elif activity_type == "message":
                    # Regular message from bot
                    if role == "bot" or role is None:
                        if text:
                            all_responses.append(text)
                else:
                    # Other activity types (event, invoke, etc.)
                    # Check ALL possible fields for thinking data
                    name = getattr(activity, "name", None)
                    if name and ("thinking" in name.lower() or "reasoning" in name.lower()):
                        thinking_text.append(f"[{name}]")

                    # Check channel_data for thinking/reasoning
                    channel_data = getattr(activity, "channel_data", None)
                    if channel_data and isinstance(channel_data, dict):
                        if "thinking" in channel_data:
                            thinking_text.append(f"[Thinking] {channel_data['thinking']}")
                        if "reasoning" in channel_data:
                            thinking_text.append(f"[Reasoning] {channel_data['reasoning']}")

                    # Check value field for additional data
                    value = getattr(activity, "value", None)
                    if value and isinstance(value, dict):
                        if "thinking" in value:
                            thinking_text.append(f"[Thinking] {value['thinking']}")
                        if "reasoning" in value:
                            thinking_text.append(f"[Reasoning] {value['reasoning']}")

                    # Check entities
                    entities = getattr(activity, "entities", None)
                    if entities:
                        for entity in entities:
                            if hasattr(entity, "type") and "thinking" in str(getattr(entity, "type", "")).lower():
                                thinking_text.append(f"[Entity Thinking] {entity}")

            # Build complete response with thinking process
            complete_response = []

            if thinking_text:
                complete_response.extend(thinking_text)
                complete_response.append("")  # Blank line separator

            if all_responses:
                complete_response.extend(all_responses)

            if complete_response:
                full_response = "\n".join(complete_response)

                # Try to parse as JSON if it looks like JSON
                if full_response.strip().startswith('{') and full_response.strip().endswith('}'):
                    try:
                        # Parse JSON and return as dict
                        parsed = json.loads(full_response)
                        print("✓ Parsed response as JSON\n")
                        return parsed
                    except json.JSONDecodeError:
                        # Not valid JSON, return as text
                        return full_response

                return full_response

            return "No response received"

        except Exception as e:
            print(f"Error in ask_question: {e}")
            import traceback
            traceback.print_exc()
            raise

    def send_message(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Synchronous wrapper for send_message_async"""
        return asyncio.run(self.send_message_async(message, conversation_id))

    async def chat_loop_async(self):
        """Interactive chat loop"""
        await self._initialize_client_async()

        print("=" * 60)
        print(f"Chat with {self.config.agent.schema_name}")
        print("=" * 60)
        print("Commands:")
        print("  - Type your message and press Enter")
        print("  - 'help' - Show this help message")
        print("  - 'exit' / 'quit' / 'bye' - End chat")
        print("=" * 60 + "\n")

        # Start conversation
        conv_result = await self.start_conversation_async()
        conversation_id = conv_result["conversation_id"]
        print(f"✓ Conversation started (ID: {conversation_id})\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\nGoodbye!\n")
                    break

                if user_input.lower() == 'help':
                    print("\nAvailable commands:")
                    print("  - Type a message to chat with the agent")
                    print("  - 'help' - Show this help message")
                    print("  - 'exit' / 'quit' / 'bye' - End chat\n")
                    continue

                # Send message and get response
                response = await self.send_message_async(user_input, conversation_id)
                print(f"\nAgent: {response}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!\n")
                break
            except Exception as e:
                print(f"\nError: {e}\n")
                import traceback
                traceback.print_exc()
                break

    def chat_loop(self):
        """Synchronous wrapper for chat_loop_async"""
        asyncio.run(self.chat_loop_async())

    def get_config_info(self) -> Dict[str, Any]:
        """Get current configuration information"""
        return {
            "agent": {
                "environment_id": self.config.agent.environment_id,
                "tenant_id": self.config.agent.tenant_id,
                "app_id": self.config.agent.app_id,
                "schema_name": self.config.agent.schema_name,
            },
            "auth": {
                "mode": self.config.auth.mode,
                "client_id": self.config.auth.client_id,
            },
            "initialized": self._initialized,
        }
