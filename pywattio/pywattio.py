"""Wattio SmartHome API wrapper"""
import json
import logging
from logging import NullHandler
import requests

WATTIO_BASE_URI = "https://api.wattio.com"
WATTIO_STATUS_URI = WATTIO_BASE_URI + "/public/v1/appliances/status"
WATTIO_DEVICES_URI = WATTIO_BASE_URI + "/public/v1/appliances"
WATTIO_POD_URI = WATTIO_BASE_URI + "/public/v1/appliances/pod/{}/{}"
WATTIO_THERMIC_MODE_URI = WATTIO_BASE_URI + "/public/v1/appliances/therm/{}/mode/{}"
WATTIO_THERMIC_TEMP_URI = WATTIO_BASE_URI + "/public/v1/appliances/therm/{}/target/{}"

WATTIO_AUTH_URI = WATTIO_BASE_URI + "/public/oauth2/authorize"
WATTIO_TOKEN_URI = WATTIO_BASE_URI + "/public/oauth2/token"

logging.getLogger(__name__).addHandler(NullHandler())
_LOGGER = logging.getLogger(__name__)


class WattioOauth2Client:
    def __init__(self, client_id, client_secret, redirect_uri="http://localhost:8080"):
        # Constructor
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_auth_uri(self):
        auth_uri = (
            WATTIO_AUTH_URI
            + "?response_type=code&client_id="
            + self.client_id
            + "&redirect_uri="
            + self.redirect_uri
        )
        return auth_uri

    def get_token(self, code):
        """Get Token from Wattio API, requieres Auth Code, Client ID and Secret."""
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }
        try:
            access_token_response = requests.post(
                WATTIO_TOKEN_URI, data=data, verify=False, allow_redirects=False
            )
            if "404" in access_token_response.text:
                _LOGGER.error("Token expired, restart the process")
                return 0
            try:
                token_json = json.loads(access_token_response.text)
                token = token_json["access_token"]
                return token
            except:
                _LOGGER.error("Error getting token")
                return 0
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Could't get TOKEN from Wattio API")
            _LOGGER.error(err)
        return


class Wattio:
    """Wattio API Class to retrieve data."""

    def __init__(self, token):
        self.token = token
        self.api_call_headers = {"Authorization": "Bearer " + self.token}

    def make_request(self, uri, type=None, ieee=None, value=None):
        if type is not None:
            uri = uri.format(str(ieee), str(value))
        try:
            api_call_response = requests.get(
                uri, headers=self.api_call_headers, verify=False
            )
            if api_call_response.status_code == 200:
                data = json.loads(api_call_response.text)
                return data
            else:
                return None
        except requests.exceptions.RequestException as err:
            return None

    def get_devices(self):
        """Get device info from Wattio API."""
        return self.make_request(WATTIO_DEVICES_URI)

    def update_wattio_data(self):
        """Get Data from WattioAPI."""
        return self.make_request(WATTIO_STATUS_URI)

    def set_switch_status(self, ieee, status):
        """Change switch status on / off."""
        return self.make_request(WATTIO_POD_URI, ieee, status)

    def set_thermic_temp(self, ieee, temp):
        """Change thermic target temp."""
        return self.make_request(WATTIO_THERMIC_TEMP_URI, ieee, temp)

    def set_thermic_mode(self, ieee, status):
        """Change thermic working mode."""
        return self.make_request(WATTIO_THERMIC_TEMP_URI, ieee, status)

