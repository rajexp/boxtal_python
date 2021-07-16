import json
import requests
import xmltodict
from requests.auth import HTTPBasicAuth

from constants import RunMode, RequestType, ResponseFormat

import sys

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

class BoxtalAPI():
    _TEST_SERVER_URL = "https://test.envoimoinscher.com"
    _PROD_SERVER_URL = "https://www.envoimoinscher.com"

    def __init__(self, mode=RunMode.TEST.value, api_version="v1", api_response_format=ResponseFormat.JSON):
        self.set_mode(mode)
        self.set_api_version(api_version)
        self.set_api_response_format(api_response_format)
        
    def set_credentials(self, user_email, password, api_key=""):
        """
        Method for setting credentials
        Params:
        user_email: string email of the boxtal account
        password: string password of the boxtal account
        api_key: API KEY/ access key of the boxtal account 
        """
        self._user_email = user_email
        self._pwd = password
        self._api_key = api_key
    
    def set_mode(self, mode):
        """
        Method for setting API module mode
        Params:
        mode: 'test' or 'prod' it chooses the boxtal environment this module interacts with
        """
        if (isinstance(mode, str) and mode==RunMode.TEST.value) or (isinstance(mode, RunMode) and mode == RunMode.TEST):
            self.server_url = self._TEST_SERVER_URL
        else:
            self.server_url = self._PROD_SERVER_URL
    
    def set_api_response_format(self, format):
        """
        Method for setting API module mode
        Params:
        format: 'JSON' or 'XML' for selecting the API output format
        """
        if (isinstance(format, str) and format.lower()==ResponseFormat.XML.value) or (isinstance(format, RunMode) and format == RunMode.XML):
            self.response_format = ResponseFormat.XML
        else:
            self.response_format = ResponseFormat.JSON

    def set_api_version(self, api_version="v1"):
        """
        Method for setting api version
        Params:
        api_version: string boxtal api version (default: v1)
        """
        self.api_version = api_version

    def _make_request(self, endpoint, type=RequestType.GET, params={}, data={}):
        url = f'{self.server_url}{endpoint}'
        if type == RequestType.GET:
            req = requests.get(url, params=params, headers={'access_key': self._api_key}, auth=HTTPBasicAuth(self._user_email, self._pwd))
        elif type == RequestType.POST:
            req = requests.post(url, params=params, data=data, headers={'access_key': self._api_key}, auth=HTTPBasicAuth(self._user_email, self._pwd))
        else:
            raise Exception("Unhandled HTTP method accessed in make_request")
        if self.response_format == ResponseFormat.JSON:
            if req.ok:
                result = {"data": json.loads(json.dumps(xmltodict(req.text))), "error": {}, "status_code": req.status_code}
            else:
                result = {"data": {},  "status_code": req.status_code}
                result.update(json.loads(json.dumps(xmltodict(req.text))))
            return req.status_code,  result
        else:
            return req.status_code, req.text

    def get_content_categories(self):
        """
        Method for getting content categories
        Returns:
        XML/JSON containing the content categories Ref: https://www.boxtal.com/fr/en/api
        """
        content_category_endpoint = f"/api/{self.api_version}/content_categories"
        return self._make_request(content_category_endpoint)

    def get_all_content(self):
        """
        Method for getting content list
        Returns:
        XML/JSON containing the content list Ref: https://www.boxtal.com/fr/en/api
        """
        content_endpoint = f"/api/{self.api_version}/content"
        return self._make_request(content_endpoint)

    def get_content_by_category(self, category_id):
        """
        Method for getting content list specific to category_id
        Returns:
        XML/JSON containing the content list specific to category id Ref: https://www.boxtal.com/fr/en/api
        """
        content_endpoint = f"/api/{self.api_version}/content_category/{category_id}/contents"
        return self._make_request(content_endpoint)

    def get_quotation(self, parameters={}):
        """
        Method for getting quotation for shipment.
        Params:
        parameters: Expecting the dictionary input consisting of the shipment related info Ref: https://www.boxtal.com/fr/en/api
        Returns:
        XML/JSON containing the  quotation response
        """
        content_endpoint = f"/api/{self.api_version}/cotation"
        return self._make_request(content_endpoint, params=parameters)

    def get_countries(self):
        """
        Method for getting countries list along with country codes
        Returns:
        XML/JSON containing list of country and country codes object.
        """
        content_endpoint = f"/api/{self.api_version}/countries"
        return self._make_request(content_endpoint)

