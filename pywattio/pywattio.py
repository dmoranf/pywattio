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
    """Wattio OAUTH2 Class."""

    def __init__(self, client_id, client_secret, redirect_uri="http://localhost:8080"):
        """Constructor method

        :param client_id: [description]
        :type client_id: str
        :param client_secret: [description]
        :type client_secret: str
        :param redirect_uri: [description], defaults to "http://localhost:8080"
        :type redirect_uri: str, optional
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_auth_uri(self):
        """Returns Wattio Auth URI

        :return: Wattio URL where you need to allow access to retrieve an auth code
        :rtype: str
        """

        auth_uri = (
            WATTIO_AUTH_URI
            + "?response_type=code&client_id="
            + self.client_id
            + "&redirect_uri="
            + self.redirect_uri
        )
        return auth_uri

    def get_token(self, code):
        """Returns a Token from Wattio API, requires Auth Code, Cliend ID and Secret,

        :param code: Auth code retrieves from Wattio API
        :type code: str
        :return: Token for API access
        :rtype: str
        """

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
    """Wrapper for Wattio's API."""

    def __init__(self, token):
        """Constructor method

        :param token: Wattio access token
        :type token: str
        """

        self.token = token
        self.api_call_headers = {"Authorization": "Bearer " + self.token}

    def make_request(self, uri, ieee=None, value=None):
        """Builds a request to Wattio API based on passed params

        :param uri: Wattio endpoint URI
        :type uri: str
        :param ieee: Device identifier (IEEE) defaults to None
        :type ieee: str, optional
        :param value: Value to send, defaults to None
        :type value: str, optional
        :return: Response data from API request
        :rtype: str
        """

        method = "GET"
        if ieee is not None:
            uri = uri.format(str(ieee), str(value))
            method = "PUT"
        try:
            api_call_response = requests.request(
                method, uri, headers=self.api_call_headers, verify=False
            )
            _LOGGER.debug("Request response code %s", api_call_response.status_code)
            if ieee is not None:
                return api_call_response.status_code
            if api_call_response.status_code == 200:
                _LOGGER.debug("Request data response %s", api_call_response.text)
                data = json.loads(api_call_response.text)
                return data
            else:
                _LOGGER.error("Something went wrong - Response code %s", api_call_response.status_code)
                return None
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Request error:  %s", err)
            return None

    def get_devices(self):
        """Gets devices info from Wattio API

        :return: json device data
        :rtype: str
        """

        return self.make_request(WATTIO_DEVICES_URI)

    def get_status(self):
        """Gets status data from Wattio API

        :return: json status data
        :rtype: str
        """

        return self.make_request(WATTIO_STATUS_URI)

    def set_switch_status(self, ieee, status):
        """Changes switch status on//ff

        :param ieee: Device id (IEEE)
        :type ieee: str
        :param status: on | off
        :type status: str
        :return:
        :rtype:
        """

        return self.make_request(WATTIO_POD_URI, ieee, status)

    def set_thermic_temp(self, ieee, temp):
        """Changes thermic target temperature

        :param ieee: Device id (IEEE)
        :type ieee: str
        :param temp: Target temperature
        :type temp: float
        :return:
        :rtype:
        """

        return self.make_request(WATTIO_THERMIC_TEMP_URI, ieee, temp)

    def set_thermic_mode(self, ieee, status):
        """Changes thermic mode

        :param ieee: Device id (IEEE)
        :type ieee: str
        :param status: Thermic mode ( 0 => Off | 1 => Manual | 2 => Auto)
        :type status: int
        :return:
        :rtype:
        """

        return self.make_request(WATTIO_THERMIC_TEMP_URI, ieee, status)
