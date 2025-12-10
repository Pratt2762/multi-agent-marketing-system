"""
Adobe Client Factory
Creates mock or real Adobe client based on configuration.
Allows seamless switching between mock (CSV) and real (API) modes.
"""

from backend.services.mock_adobe_client import MockAdobeClient
from backend.services.adobe_aep_client import AdobeAEPClient


class AdobeClientFactory:
    """
    Factory to create appropriate Adobe client (mock or real).

    Usage:
        # Mock mode (for development without Adobe credentials)
        client = AdobeClientFactory.create_client(use_mock=True)

        # Real mode (for production with Adobe credentials)
        client = AdobeClientFactory.create_client(
            use_mock=False,
            api_key="...",
            org_id="...",
            ...
        )
    """

    @staticmethod
    def create_client(use_mock=True, data_dir="data", **adobe_credentials):
        """
        Create Adobe client (mock or real).

        Args:
            use_mock: If True, use mock client with CSV data
            data_dir: Directory containing CSV files (for mock mode)
            **adobe_credentials: Adobe API credentials (for real mode):
                - api_key
                - org_id
                - technical_account_id
                - private_key
                - client_secret

        Returns:
            MockAdobeClient or AdobeAEPClient instance
        """
        if use_mock:
            print("🔧 Using MOCK Adobe client (CSV-based simulation)")
            return MockAdobeClient(data_dir=data_dir)
        else:
            print("🔧 Using REAL Adobe AEP/RT-CDP client (API-based)")

            # Validate required credentials
            required = ['api_key', 'org_id', 'technical_account_id', 'private_key', 'client_secret']
            missing = [k for k in required if k not in adobe_credentials]

            if missing:
                raise ValueError(f"Missing Adobe credentials: {', '.join(missing)}")

            return AdobeAEPClient(
                api_key=adobe_credentials['api_key'],
                org_id=adobe_credentials['org_id'],
                technical_account_id=adobe_credentials['technical_account_id'],
                private_key=adobe_credentials['private_key'],
                client_secret=adobe_credentials['client_secret']
            )
