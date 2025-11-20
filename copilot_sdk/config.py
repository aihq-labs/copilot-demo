"""
Configuration management for Microsoft Copilot Agent SDK

Copyright 2025 AIHQ.ie
Licensed under the Apache License, Version 2.0
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class AgentConfig:
    """Agent configuration data"""
    environment_id: str
    tenant_id: str
    app_id: str
    schema_name: str
    name: str = "Copilot Agent"
    instructions: str = "You are a helpful AI assistant."


@dataclass
class AuthConfig:
    """Authentication configuration"""
    mode: str = "interactive"
    client_id: Optional[str] = None


@dataclass
class APIConfig:
    """API configuration"""
    base_url: str = "https://api.copilotstudio.microsoft.com"
    timeout: int = 30
    max_retries: int = 3
    cloud: str = "COMMERCIAL"  # Power Platform Cloud


class CopilotConfig:
    """
    Configuration manager for Copilot Agent SDK

    Loads configuration from:
    1. config.yaml file
    2. Environment variables (override config.yaml)
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration

        Args:
            config_path: Path to config.yaml file (optional). 
                        If None, searches in current directory.
                        If not found, uses .env file only (recommended).
        """
        self.config_path = config_path or self._find_config_file()
        self.config_data = self._load_config()

        # Parse configuration sections
        self.agent = self._parse_agent_config()
        self.auth = self._parse_auth_config()
        self.api = self._parse_api_config()

    def _find_config_file(self) -> Optional[str]:
        """Find config.yaml in current or parent directories (optional)"""
        current = Path.cwd()
        for _ in range(3):  # Search up to 3 levels
            config_file = current / "config.yaml"
            if config_file.exists():
                return str(config_file)
            current = current.parent

        # config.yaml is optional - return None if not found
        return None

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file (optional - .env is primary)"""
        if not self.config_path:
            return {}  # config.yaml is optional
        
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            # config.yaml is optional - no warning needed
            return {}
        except yaml.YAMLError as e:
            print(f"Warning: Error parsing config.yaml: {e}")
            return {}

    def _parse_agent_config(self) -> AgentConfig:
        """Parse agent configuration - environment variables take priority"""
        agent_data = self.config_data.get('agent', {})

        return AgentConfig(
            environment_id=os.getenv(
                'COPILOT_STUDIO_AGENT_ENVIRONMENT_ID',
                agent_data.get('environment_id') or ''
            ),
            tenant_id=os.getenv(
                'COPILOT_STUDIO_AGENT_TENANT_ID',
                agent_data.get('tenant_id') or ''
            ),
            app_id=os.getenv(
                'COPILOT_STUDIO_AGENT_APP_ID',
                agent_data.get('app_id') or ''
            ),
            schema_name=os.getenv(
                'COPILOT_STUDIO_AGENT_AGENT_IDENTIFIER',
                agent_data.get('schema_name') or ''
            ),
            name=os.getenv(
                'COPILOT_STUDIO_AGENT_NAME',
                agent_data.get('name', 'Copilot Agent')
            ),
            instructions=os.getenv(
                'COPILOT_STUDIO_AGENT_INSTRUCTIONS',
                agent_data.get('instructions', 'You are a helpful AI assistant.')
            )
        )

    def _parse_auth_config(self) -> AuthConfig:
        """Parse authentication configuration with environment variable overrides"""
        auth_data = self.config_data.get('auth', {})

        return AuthConfig(
            mode=os.getenv(
                'COPILOT_STUDIO_AGENT_AUTH_MODE',
                auth_data.get('mode', 'interactive')
            ),
            client_id=os.getenv(
                'COPILOT_STUDIO_AGENT_APP_CLIENT_ID',
                auth_data.get('client_id')
            )
        )

    def _parse_api_config(self) -> APIConfig:
        """Parse API configuration - environment variables take priority"""
        api_data = self.config_data.get('api', {})

        return APIConfig(
            base_url=os.getenv(
                'COPILOT_STUDIO_API_BASE_URL',
                api_data.get('base_url', 'https://api.copilotstudio.microsoft.com')
            ),
            timeout=int(os.getenv(
                'COPILOT_STUDIO_API_TIMEOUT',
                api_data.get('timeout', 30)
            )),
            max_retries=int(os.getenv(
                'COPILOT_STUDIO_API_MAX_RETRIES',
                api_data.get('max_retries', 3)
            )),
            cloud=os.getenv(
                'POWER_PLATFORM_CLOUD',
                api_data.get('cloud', 'PROD')
            )
        )

    def validate(self) -> bool:
        """
        Validate configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        errors = []

        if not self.agent.environment_id:
            errors.append("Missing environment_id")
        if not self.agent.tenant_id:
            errors.append("Missing tenant_id")
        if not self.agent.schema_name:
            errors.append("Missing schema_name")

        # Validate auth mode
        valid_auth_modes = ["directline", "interactive", "client_credentials"]
        if self.auth.mode not in valid_auth_modes:
            errors.append(f"Invalid auth mode '{self.auth.mode}'. Must be one of: {', '.join(valid_auth_modes)}")

        # Client ID is required for MSAL auth modes (not directline)
        if self.auth.mode in ["interactive", "client_credentials"] and not self.auth.client_id:
            errors.append(f"Missing client_id for auth mode '{self.auth.mode}' (set COPILOT_STUDIO_AGENT_APP_CLIENT_ID)")

        # DirectLine secret required for directline mode
        if self.auth.mode == "directline":
            directline_secret = os.getenv("COPILOT_STUDIO_WEB_CHANNEL_SECURITY_KEY")
            if not directline_secret:
                errors.append("Missing DirectLine secret (set COPILOT_STUDIO_WEB_CHANNEL_SECURITY_KEY)")

        if errors:
            print("Configuration validation failed:")
            for error in errors:
                print(f"  - {error}")
            return False

        return True

    def display(self):
        """Display current configuration (with sensitive data masked)"""
        print("=" * 60)
        print("Copilot Agent Configuration")
        print("=" * 60)
        print(f"Agent:")
        print(f"  Environment ID: {self.agent.environment_id}")
        print(f"  Tenant ID: {self.agent.tenant_id}")
        print(f"  App ID: {self.agent.app_id}")
        print(f"  Schema Name: {self.agent.schema_name}")
        print(f"  Name: {self.agent.name}")
        print(f"\nAuthentication:")
        print(f"  Mode: {self.auth.mode}")
        print(f"  Client ID: {'***' + self.auth.client_id[-8:] if self.auth.client_id else 'Not set'}")
        print(f"\nAPI:")
        print(f"  Base URL: {self.api.base_url}")
        print(f"  Timeout: {self.api.timeout}s")
        print("=" * 60)
