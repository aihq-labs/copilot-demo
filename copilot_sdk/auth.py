"""
Authentication handling for Microsoft Copilot Agent SDK

Copyright 2025 AIHQ.ie
Licensed under the Apache License, Version 2.0
"""

import os
from typing import Optional
from azure.identity import (
    DeviceCodeCredential,
    ClientSecretCredential,
    DefaultAzureCredential
)


class CopilotAuthenticator:
    """
    Handles authentication for Microsoft Copilot Studio agents

    Supports multiple authentication methods:
    - None (no authentication required)
    - Interactive (Device Code Flow)
    - Client Credentials (Service Principal)
    - Default Azure Credential Chain
    """

    def __init__(self, tenant_id: str, client_id: Optional[str] = None, auth_mode: str = "none"):
        """
        Initialize authenticator

        Args:
            tenant_id: Azure AD tenant ID
            client_id: Azure AD application client ID (not required for "none" mode)
            auth_mode: Authentication mode ("none", "interactive", "client_credentials", "default")
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.auth_mode = auth_mode
        self._credential = None

    def get_credential(self):
        """
        Get Azure credential based on auth mode

        Returns:
            Azure credential object or None if auth mode is "none"
        """
        if self.auth_mode == "none":
            return None

        if self._credential:
            return self._credential

        if self.auth_mode == "interactive":
            self._credential = self._get_device_code_credential()
        elif self.auth_mode == "client_credentials":
            self._credential = self._get_client_secret_credential()
        elif self.auth_mode == "default":
            self._credential = self._get_default_credential()
        else:
            raise ValueError(f"Unknown auth mode: {self.auth_mode}")

        return self._credential

    def _get_device_code_credential(self):
        """
        Get Device Code credential for interactive authentication

        This will prompt the user to visit a URL and enter a code
        """
        print(f"\nInitializing Device Code authentication...")
        print(f"Tenant ID: {self.tenant_id}")
        print(f"Client ID: {self.client_id}")

        return DeviceCodeCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            # Callback to display the device code prompt
            prompt_callback=self._device_code_prompt
        )

    def _get_client_secret_credential(self):
        """
        Get Client Secret credential for non-interactive authentication

        Requires AZURE_CLIENT_SECRET environment variable
        """
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        if not client_secret:
            raise ValueError(
                "AZURE_CLIENT_SECRET environment variable required for client_credentials auth mode"
            )

        print(f"\nUsing Client Secret authentication...")

        return ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=client_secret
        )

    def _get_default_credential(self):
        """
        Get Default Azure credential

        Uses Azure credential chain (environment variables, managed identity, CLI, etc.)
        """
        print(f"\nUsing Default Azure credential chain...")

        return DefaultAzureCredential()

    @staticmethod
    def _device_code_prompt(verification_uri: str, user_code: str, expires_in: int):
        """
        Display device code authentication prompt

        Args:
            verification_uri: URL to visit for authentication
            user_code: Code to enter
            expires_in: Expiration time in seconds
        """
        print("\n" + "=" * 60)
        print("DEVICE CODE AUTHENTICATION")
        print("=" * 60)
        print(f"\nTo sign in, use a web browser to open the page:")
        print(f"\n  {verification_uri}")
        print(f"\nAnd enter the code:")
        print(f"\n  {user_code}")
        print(f"\nThis code expires in {expires_in // 60} minutes.")
        print("=" * 60 + "\n")

    def get_access_token(self, scopes: Optional[list] = None) -> Optional[str]:
        """
        Get access token for API calls

        Args:
            scopes: List of OAuth scopes

        Returns:
            Access token string or None if auth mode is "none"
        """
        if self.auth_mode == "none":
            return None

        if scopes is None:
            # Default scope for Copilot Studio
            scopes = ["https://api.copilotstudio.microsoft.com/.default"]

        credential = self.get_credential()
        token = credential.get_token(*scopes)
        return token.token

    def is_auth_required(self) -> bool:
        """
        Check if authentication is required

        Returns:
            True if authentication is required, False otherwise
        """
        return self.auth_mode != "none"
