import requests
from requests.auth import HTTPBasicAuth
from constants import RunMode, RequestType

import sys

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

class BoxtalAPI():
    _TEST_SERVER_URL = "https://test.envoimoinscher.com"
    _PROD_SERVER_URL = "https://www.envoimoinscher.com"

    def __init__(self, mode=RunMode.TEST.value, api_version="v1"):
        self.set_mode(mode)
        self.set_api_version(api_version)
        
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
        if mode==RunMode.TEST.value:
            self.server_url = self._TEST_SERVER_URL
        else:
            self.server_url = self._PROD_SERVER_URL
    
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
        return req.status_code, req.text

    def get_content_categories(self):
        """
        Method for getting content categories
        Returns:
        XML string containing the content categories Ref: https://www.boxtal.com/fr/en/api
        """
        content_category_endpoint = f"/api/{self.api_version}/content_categories"
        return self._make_request(content_category_endpoint)

    def get_all_content(self):
        """
        Method for getting content list
        Returns:
        XML string containing the content list Ref: https://www.boxtal.com/fr/en/api
        """
        content_endpoint = f"/api/{self.api_version}/content"
        return self._make_request(content_endpoint)

