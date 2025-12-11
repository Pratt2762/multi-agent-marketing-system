"""
Real Adobe AEP/RT-CDP Client (Skeleton for future implementation)
Connects to Adobe Experience Platform and Real-Time CDP via REST APIs.

Data Sources:
- Adobe Experience Platform (AEP): Campaign and ad group performance
- Adobe Real-Time CDP (RT-CDP): Audience segments and profiles

Authentication: JWT-based OAuth 2.0 (Adobe I/O)
"""

import requests
import jwt
import time
from datetime import datetime, timedelta
from backend.services.adobe_data_translator import AdobeDataTranslator


class AdobeAEPClient:
    """
    Real Adobe Experience Platform and RT-CDP client.

    Architecture:
    1. Authenticate with Adobe I/O (JWT tokens)
    2. Fetch data from AEP and RT-CDP APIs
    3. Use same translator as mock client (downstream code unchanged)

    Requires Adobe credentials:
    - API Key
    - Organization ID
    - Technical Account ID
    - Private Key (RSA)
    - Client Secret
    """

    def __init__(self, api_key, org_id, technical_account_id, private_key, client_secret):
        """
        Initialize Adobe AEP/RT-CDP client with credentials.

        Args:
            api_key: Adobe API key (from Adobe Developer Console)
            org_id: Adobe Organization ID
            technical_account_id: Adobe Technical Account ID
            private_key: RSA private key for JWT signing
            client_secret: Adobe client secret
        """
        self.api_key = api_key
        self.org_id = org_id
        self.technical_account_id = technical_account_id
        self.private_key = private_key
        self.client_secret = client_secret
        self.access_token = None

        # Adobe endpoints
        self.aep_base_url = "https://platform.adobe.io"
        self.ims_url = "https://ims-na1.adobelogin.com"

        # Authenticate on initialization
        self._authenticate()

        print("[INIT] Adobe AEP/RT-CDP Client initialized (Real API mode)")

    def _authenticate(self):
        """
        Authenticate with Adobe I/O using JWT tokens.

        Flow:
        1. Create JWT with credentials
        2. Sign JWT with private key
        3. Exchange JWT for access token
        4. Use access token for API calls
        """
        # JWT payload
        payload = {
            "exp": int(time.time()) + 86400,  # 24 hours
            "iss": self.org_id,
            "sub": self.technical_account_id,
            "aud": f"{self.ims_url}/c/{self.api_key}",
            f"{self.ims_url}/s/ent_dataservices_sdk": True
        }

        # Create JWT (signed with private key)
        encoded_jwt = jwt.encode(payload, self.private_key, algorithm='RS256')

        # Exchange JWT for access token
        token_url = f"{self.ims_url}/ims/exchange/jwt"
        data = {
            'client_id': self.api_key,
            'client_secret': self.client_secret,
            'jwt_token': encoded_jwt
        }

        response = requests.post(token_url, data=data)
        response.raise_for_status()

        self.access_token = response.json()['access_token']
        print("[OK] Adobe authentication successful")

    def _make_api_call(self, method, endpoint, payload=None):
        """
        Make authenticated API call to Adobe.

        Args:
            method: HTTP method (GET, POST, PATCH)
            endpoint: API endpoint path
            payload: Request body (for POST/PATCH)

        Returns:
            JSON response from Adobe API
        """
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'x-api-key': self.api_key,
            'x-gw-ims-org-id': self.org_id,
            'Content-Type': 'application/json'
        }

        url = f"{self.aep_base_url}{endpoint}"

        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=payload)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=payload)

        response.raise_for_status()
        return response.json()

    # ========== DATA FETCHING (AEP + RT-CDP) ==========

    def get_campaign_data(self, days_back=14):
        """
        Fetch campaign data from Adobe Experience Platform.

        Source: Adobe Campaign Standard/Classic API
        Endpoint: GET /campaign/performance
        Returns: pandas DataFrame (via translator)
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        endpoint = f"/campaign/performance?start={start_date.isoformat()}&end={end_date.isoformat()}"
        adobe_response = self._make_api_call('GET', endpoint)

        # Translate to DataFrame (same format as mock)
        return AdobeDataTranslator.translate_campaigns(adobe_response)

    def get_ad_group_metrics(self):
        """
        Fetch ad group data from Adobe Experience Platform.

        Source: AEP Query Service (via Google Ads/Meta Source Connectors)
        Endpoint: GET /data/foundation/query/adgroups
        Returns: pandas DataFrame (via translator)
        """
        endpoint = "/data/foundation/query/adgroups"
        adobe_response = self._make_api_call('GET', endpoint)

        # Translate to DataFrame (same format as mock)
        return AdobeDataTranslator.translate_ad_groups(adobe_response)

    def get_audience_segments(self):
        """
        Fetch audience segments from Adobe Real-Time CDP.

        Source: RT-CDP Unified Profile Service (UPS)
        Endpoint: GET /data/core/ups/segment/definitions
        Returns: pandas DataFrame (via translator)
        """
        endpoint = "/data/core/ups/segment/definitions"
        adobe_response = self._make_api_call('GET', endpoint)

        # Translate to DataFrame (same format as mock)
        return AdobeDataTranslator.translate_audiences(adobe_response)

    # ========== EXECUTION METHODS (Write to Adobe) ==========

    def update_campaign_budget(self, campaign_id, new_budget):
        """
        Update campaign budget in Adobe Campaign.

        Endpoint: PATCH /campaign/{campaignId}
        """
        endpoint = f"/campaign/{campaign_id}"
        payload = {"budget": {"allocated": new_budget}}
        return self._make_api_call('PATCH', endpoint, payload)

    def update_bid_strategy(self, ad_group_id, new_bid):
        """
        Update ad group bid via Adobe Destination Connectors.

        Endpoint: PATCH /adGroups/{adGroupId}/bidding
        """
        endpoint = f"/adGroups/{ad_group_id}/bidding"
        payload = {"averageBid": new_bid}
        return self._make_api_call('PATCH', endpoint, payload)

    def activate_segment(self, segment_id):
        """
        Activate audience segment in Adobe Real-Time CDP.

        Endpoint: POST /data/core/ups/segment/jobs
        """
        endpoint = f"/data/core/ups/segment/jobs"
        payload = {
            "segmentId": segment_id,
            "action": "activate"
        }
        return self._make_api_call('POST', endpoint, payload)

    def suppress_segment(self, segment_id):
        """
        Deactivate audience segment in Adobe Real-Time CDP.

        Endpoint: POST /data/core/ups/segment/jobs
        """
        endpoint = f"/data/core/ups/segment/jobs"
        payload = {
            "segmentId": segment_id,
            "action": "deactivate"
        }
        return self._make_api_call('POST', endpoint, payload)
