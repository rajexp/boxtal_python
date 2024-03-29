import json
import requests
import xmltodict
from requests.auth import HTTPBasicAuth

from constants import RunMode, RequestType, ResponseFormat

import sys
import logging

logging.basicConfig(level=logging.INFO)

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
    
    def set_api_response_format(self, format=ResponseFormat.XML):
        """
        Method for setting API module mode
        Params:
        format: 'JSON' or 'XML' for selecting the API output format
        """
        if (isinstance(format, str) and format.lower()==ResponseFormat.XML.value) or (isinstance(format, ResponseFormat) and format==ResponseFormat.XML):
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
        url = '{}{}'.format(self.server_url, endpoint)
        if type == RequestType.GET:
            req = requests.get(url, params=params, headers={'access_key': self._api_key}, auth=HTTPBasicAuth(self._user_email, self._pwd))
        elif type == RequestType.POST:
            req = requests.post(url, params=params, data=data, headers={'access_key': self._api_key}, auth=HTTPBasicAuth(self._user_email, self._pwd))
        else:
            raise Exception("Unhandled HTTP method accessed in make_request")
        logging.info(" {}: {} Payload: {}".format(req.request.method, req.url, req.request.body))
        if self.response_format == ResponseFormat.JSON:
            if req.ok:
                result = {"data": json.loads(json.dumps(xmltodict.parse(req.text))), "error": {}, "status_code": req.status_code}
            else:
                result = {"data": {},  "status_code": req.status_code}
                text = req.text
                result.update(json.loads(json.dumps(xmltodict.parse(text))))
            return req.status_code,  result
        else:
            return req.status_code, req.text

    def get_content_categories(self):
        """
        Method for getting content categories
        Returns:
        XML/JSON containing the content categories Ref: https://www.boxtal.com/fr/en/api
        """
        content_category_endpoint = "/api/{}/content_categories".format(self.api_version)
        return self._make_request(content_category_endpoint)

    def get_all_content(self):
        """
        Method for getting content list
        Returns:
        XML/JSON containing the content list Ref: https://www.boxtal.com/fr/en/api
        """
        content_endpoint = "/api/{}/contents".format(self.api_version)
        return self._make_request(content_endpoint)

    def get_content_by_category(self, category_id):
        """
        Method for getting content list specific to category_id
        Returns:
        XML/JSON containing the content list specific to category id Ref: https://www.boxtal.com/fr/en/api
        """
        content_endpoint = "/api/{}/content_category//contents".format(self.api_version, category_id)
        return self._make_request(content_endpoint)

    def get_quotation(self, from_, to, parcels, additional_parameters={}):
        """
        Method for getting quotation for shipment.
        Params:
        from_: the sender info or sender object
        to: the receiver info or receiver object
        parcels: the parcel information
        additional_parameters: Expecting the dictionary input consisting of the shipment related info Ref: https://www.boxtal.com/fr/en/api
        Returns:
        XML/JSON containing the  quotation response
        """
        parameters = {}
        if isinstance(from_, self.Sender):
            parameters.update(from_.jsonify())
        else:
            parameters.update(from_)
        if isinstance(to, self.Person):
            parameters.update(to.jsonify())
        else:
            parameters.update(to)
        parameters.update(self.create_package_param_dict(parcels))
        parameters.update(additional_parameters)
        content_endpoint = "/api/{}/cotation".format(self.api_version)
        return self._make_request(content_endpoint, params=parameters)

    def get_countries(self):
        """
        Method for getting countries list along with country codes
        Returns:
        XML/JSON containing list of country and country codes object.
        """
        content_endpoint = "/api/{}/countries".format(self.api_version)
        return self._make_request(content_endpoint)

    def get_pickup_point_info(self, point_code):
        """
        Method for getting arrival relay points
        Returns:
        XML/JSON Dictionary of arrival relay points
        """
        url_endpoint = "/api/{}/pickup_point/{}/informations".format(self.api_version, point_code)
        return self._make_request(url_endpoint)

    def get_dropoff_point_info(self, point_code):
        """
        Method for getting of departure relay points
        Returns:
        XML/JSON Dictionary of departure relay points
        """
        url_endpoint = "/api/{}/dropoff_point/{}/informations".format(self.api_version, point_code)
        return self._make_request(url_endpoint)

    def create_order(self, from_, to, parcels, additional_parameters={}):
        """
        Method for creating package order
        Params:
        from_: the sender info or sender object
        to: the receiver info or receiver object
        parcels: the parcel information
        additional_parameters: Expecting the dictionary input consisting of the shipment related info Ref: https://www.boxtal.com/fr/en/api
        Returns:
        XML/JSON containing order information
        """
        parameters = { "platform": "api", "platform_version": "1"}
        if isinstance(from_, self.Sender):
            parameters.update(from_.jsonify())
        else:
            parameters.update(from_)
        if isinstance(to, self.Person):
            parameters.update(to.jsonify())
        else:
            parameters.update(to)
        parameters.update(self.create_package_param_dict(parcels))
        parameters.update(additional_parameters)

        url_endpoint = "/api/{}/order".format(self.api_version)
        return  self._make_request(url_endpoint, type=RequestType.POST, params=parameters)

    def get_order_status(self, order_reference):
        """
        Method for checking real time order status placed via API
        Params:
        order_reference:string the order refernce you get from the order api
        Returns:
        XML/JSON containing real time order status info.
        """
        url_endpoint = "/api/{}/order_status/{}/informations".format(self.api_version, order_reference)
        return self._make_request(url_endpoint)


    class Person():
        def __init__(self, title="", name="", surname="", type="", company_name="", email="", tel="", country_code="", postal_code="",  city="", address="", address_additional_info=""):
            """
            Base class for the sender and receiver entity
            Param
            type: 'particulier' or 'entreprise'
            company_name: Required if sender_type is ‘entreprise’
            """
            self.country_code = country_code
            self.postal_code = postal_code
            self.type = type
            self.company_name = company_name
            self.city = city
            self.address = address
            self.address_additional_info = address_additional_info
            self.title = title
            self.name = name
            self.surname = surname
            self.email = email
            self.tel = tel


    class Sender(Person):
        def jsonify(self):
            return {"expediteur.type": self.type, "expediteur.pays": self.country_code, "expediteur.code_postal": self.postal_code,
            "expediteur.ville": self.city, "expediteur.adresse": self.address,  "expediteur.civilite": self.title,
            "expediteur.prenom": self.name, "expediteur.nom": self.surname, "expediteur.email": self.email,
            "expediteur.tel": self.tel, "expediteur.infos": self.address_additional_info}


    class Receiver(Person):
        def jsonify(self):
            return {"destinataire.type": self.type, "destinataire.pays": self.country_code, "destinataire.code_postal": self.postal_code,
            "destinataire.ville": self.city, "destinataire.adresse": self.address,  "destinataire.civilite": self.title,
            "destinataire.prenom": self.name, "destinataire.nom": self.surname, "destinataire.email": self.email,
            "destinataire.tel": self.tel, "destinataire.infos": self.address_additional_info}

    @staticmethod
    def create_package_param_dict(packages):
        out_dict = {}
        for index, package_info in enumerate(packages):
            package_type = package_info.get("type")
            package_prefix = '{}_{}'.format(package_type, index+1)
            out_dict.update({'{}.poids'.format(package_prefix): package_info['poids'], '{}.longueur'.format(package_prefix): package_info['longueur'],
                '{}.largeur'.format(package_prefix): package_info['largeur']})
            if package_info.get("description"): # Required for order
                out_dict.update({"{}.description".format(package_type): package_info["description"]})
            if package_info.get("value"):
                out_dict['{}.valeur'.format(package_type)] = out_dict.get('{}.valeur'.format(package_type), 0) + float(package_info.get("value"))
            # Since hauteur is only applicable for package of type except pli
            if package_info["type"] != "pli":
                out_dict.update({'{}.hauteur'.format(package_prefix): package_info['hauteur']})
        return out_dict