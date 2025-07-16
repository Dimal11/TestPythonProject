import os
import requests
from loguru import logger

class RevcontentAPI:
    """
        Client for interacting with the Revcontent API.

        This class provides methods for authenticating via OAuth2,
        creating new advertising campaigns (Boosts), and retrieving
        campaign statistics using the Revcontent API.

        Attributes:
            client_id (str): The client ID for API authentication.
            client_secret (str): The client secret for API authentication.
            access_token (str): The OAuth2 access token, set after authentication.
    """

    def __init__(self, client_id, client_secret):
        """
            Initializes the RevcontentAPI client.

            Args:
                client_id (str): The client ID for API authentication.
                client_secret (str): The client secret for API authentication.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def auth(self) -> None:
        """
            Authenticates with the Revcontent API using client credentials.

            Requests an access token and stores it for future API requests.

            Raises:
                Exception: If authentication fails or no access token is returned.
                ValueError: If a 400 Bad Request is returned by the API, with detailed error description.
        """
        url = f'{os.getenv("API_URL")}/oauth/token'
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache"
        }
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        logger.info("Authenticating with Revcontent API...")
        resp = requests.post(url=url, json=payload, headers=headers)
        if resp.status_code == 200:
            self.access_token = resp.json().get('access_token')
            if not self.access_token:
                logger.error("Access token not found in response.")
                raise Exception("Access token not found in response.")
            logger.success("Authentication successful.")
        elif resp.status_code == 400:
            error = resp.json().get('error', 'unknown_error')
            error_description = resp.json().get('error_description', 'No description provided.')
            logger.error(f"Authentication failed with 400 Bad Request: {error} - {error_description}")
            raise ValueError(f"Authentication failed with 400 Bad Request: {error} - {error_description}")
        else:
            logger.error(f"Authentication failed: {resp.status_code} {resp.text}")
            raise Exception(f"Authentication failed: {resp.status_code} {resp.text}")

    def create_campaign(self, name: str, budget: float, bid: float, countries: list) -> str:
        """
            Creates a new campaign (Boost) in Revcontent.

            Args:
                name (str): The name of the campaign.
                budget (float): Total campaign budget in USD.
                bid (float): Default bid per click in USD.
                countries (list of str): List of country codes to target.

            Returns:
                str: The ID of the created campaign.

            Raises:
                Exception: If campaign creation fails.
                ValueError: If a 400 Bad Request is returned by the API, with details about the error.
        """
        if not self.access_token:
            logger.error("Not authenticated. Call authenticate() first.")
            raise Exception("Not authenticated. Call authenticate() first.")
        url = f'{os.getenv("API_URL")}/stats/api/v1.0/boosts/add'
        payload = {
            "name": name,
            "budget": budget,
            "bid_amount": bid,
            "country_codes": countries
        }
        logger.info(f"Creating campaign: {name} (budget: {budget}, bid: {bid}, countries: {countries})")
        resp = requests.post(url, json=payload, headers=self._get_headers())
        if resp.status_code == 200 or resp.status_code == 201:
            resp_json = resp.json()
            data = resp_json.get('data')
            if isinstance(data, list) and data and 'id' in data[0]:
                logger.success(f"Campaign created successfully, ID: {data[0]['id']}")
                return data[0]['id']
            else:
                logger.error("Create campaign response does not contain campaign ID.")
                raise Exception("Create campaign response does not contain campaign ID.")
        else:
            RevcontentAPI._handle_api_error(resp)

    def get_campaign_stats_by_id(self, campaign_id: str) -> list[dict] | None:
        """
            Fetches statistics for a given campaign ID.

            Args:
                campaign_id (str): The unique ID of the campaign.

            Returns:
                list of dict: List of statistics dictionaries (impressions, clicks, etc.) for the campaign.

            Raises:
                Exception: If the user is not authenticated or if the API request fails.
                ValueError: If a 400 Bad Request is returned by the API, with details about the error.
        """
        if not self.access_token:
            logger.error("Not authenticated. Call authenticate() first.")
            raise Exception("Not authenticated. Call authenticate() first.")

        url = f'{os.getenv("API_URL")}/stats/api/v1.0/boosts/performance'
        params = {
            "boost_id": campaign_id
        }
        logger.info(f"Fetching stats for campaign: {campaign_id}")
        resp = requests.get(
            url=url,
            headers=self._get_headers(),
            params=params
        )
        if resp.status_code == 200:
            data = resp.json().get('data')
            if data is not None:
                logger.success(f"Stats received for campaign {campaign_id}: {data}")
                return data
            else:
                logger.error('Response JSON does not contain "data" key.')
                raise Exception('Response JSON does not contain "data" key.')
        else:
            RevcontentAPI._handle_api_error(resp)
            return None

    def _get_headers(self) -> dict:
        """
            Builds and returns the default headers for API requests.

            Returns:
                dict: A dictionary containing HTTP headers including
                Authorization, Content-Type, and Cache-Control.
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-type": "application/json",
            "Cache-Control": "no-cache"
        }

    @staticmethod
    def _handle_api_error(resp) -> None:
        """
        Handles errors from API responses.

        Args:
            resp (requests.Response): The response object.

        Raises:
            ValueError: For 400 Bad Request with structured error details.
            Exception: For all other error codes.
        """
        from loguru import logger
        if resp.status_code == 400:
            try:
                error_json = resp.json()
                if "errors" in error_json and isinstance(error_json["errors"], list):
                    error_messages = []
                    for err in error_json["errors"]:
                        code = err.get("code", "Unknown code")
                        title = err.get("title", "Unknown title")
                        detail = err.get("detail", "No details provided")
                        error_messages.append(f"[{code}] {title} - {detail}")
                    all_errors = "; ".join(error_messages)
                    logger.error(f"400 Bad Request: {all_errors}")
                    raise ValueError(f"400 Bad Request: {all_errors}")
                else:
                    logger.error(f"400 Bad Request: {resp.text}")
                    raise ValueError(f"400 Bad Request: {resp.text}")
            except Exception:
                logger.error(f"400 Bad Request: {resp.text}")
                raise ValueError(f"400 Bad Request: {resp.text}")
        else:
            logger.error(f"API request failed: {resp.status_code} {resp.text}")
            raise Exception(f"API request failed: {resp.status_code} {resp.text}")
