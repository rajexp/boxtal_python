import json
from boxtal import BoxtalAPI
from constants import RunMode, ResponseFormat

# Set credentials below
USER_EMAIL = ""
USER_PASSWORD = ""
API_KEY = ""

def create_package_param_dict(packages):
    out_dict = {}
    for index, package_info in enumerate(packages):
        package_prefix = '{}_{}'.format(package_info.get("type"), index+1)
        out_dict.update({'{}.poids'.format(package_prefix): package_info['poids'], '{}.longueur'.format(package_prefix): package_info['longueur'],
            '{}.largeur'.format(package_prefix): package_info['largeur']})
        if package_info.get("description"): # Required for order
            out_dict.update({"{}.description".format(package_info.get("type")): package_info["description"]})

        # Since hauteur is only applicable for package of type except pli
        if package_info["type"] != "pli":
            out_dict.update({'{}.hauteur'.format(package_prefix): package_info['hauteur']})
    return out_dict

if __name__ == '__main__':
    api = BoxtalAPI()
    api.set_mode(RunMode.TEST.value)
    api.set_credentials(USER_EMAIL, USER_PASSWORD, api_key=API_KEY)
    api.set_api_response_format(ResponseFormat.JSON)

    _, content_categories = api.get_content_categories() 
    _, content = api.get_all_content()

    # Example of quotation
    # You can add multiple packages below
    packages = [{"type": "colis", "poids": 3, "longueur": 7, "largeur": 8, "hauteur":11},
                {"type": "pli", "poids": 10, "longueur": 6, "largeur": 8}]
    package_type_value_in_euros = {"colis": 10, "pli": 8} # Save the different package type value in euros
    content_code = "10120"
    sender_country_code = "FR"
    sender_postal_code = "44000"
    sender_type = "particulier" # ‘particulier’ or ‘entreprise’
    receiver_country_code = "FR"
    receiver_postal_code = "75002"
    receiver_type = "particulier" # ‘particulier’ or ‘entreprise’
    collection_date = "2021-07-18" # YYYY-MM-DD format
    delay = "aucun" # 'aucun', ‘minimum’ or ‘course’
    quotation_parameters = {
        "code_contenu": content_code,
        "expediteur.type": sender_type, "expediteur.pays": sender_country_code, "expediteur.code_postal": sender_postal_code,
        "destinataire.type": sender_type, "destinataire.pays": sender_country_code, "destinataire.code_postal": sender_postal_code,
        "collecte": collection_date, "delai": delay}
    # Preparing the package parameters which are of type <type>_N.<poids/longueur/largeur/hauteur>
    quotation_parameters.update(create_package_param_dict(packages))
    for package_type, money_value in package_type_value_in_euros.items():
        quotation_parameters.update({'{}.valeur'.format(package_type): money_value})
    _, quotation = api.get_quotation(parameters=quotation_parameters)

    _, countries = api.get_countries()

    # Example of order API and order status API
    platform="api"
    sender_country_code = "FR"
    sender_postal_code = "44000"
    sender_type = "particulier" # ‘particulier’ or ‘entreprise’
    sender_company_name ="" # Required if sender_type is ‘entreprise’
    sender_city = "Paris"
    sender_address = "Some address here"
    sender_address_additional_info = ""
    sender_title = "Mr"
    sender_name = "Nikola"
    sender_surname = "Tesla"
    sender_email = "example@example.com"
    sender_tel = "000000000"
    receiver_country_code = "US"
    receiver_postal_code = "75002"
    receiver_type = "particulier" # ‘particulier’ or ‘entreprise’
    receiver_company_name ="" # Required if receiver_type is ‘entreprise’
    receiver_city = "New York"
    receiver_address = "Some address here"
    receiver_address_additional_info = ""
    receiver_title = "Mr"
    receiver_name = "Nikola"
    receiver_surname = "Tesla"
    receiver_email = "example@example.com"
    receiver_tel = "000000000"
    delay = "aucun" # 'aucun', ‘minimum’ or ‘course’
    content_code = "10120"
    collection_date = "2021-07-21" # YYYY-MM-DD format

    # Information to be selected from quotation API offer
    # This need to be set according to selected offer or you may have some preference set of service operators to select from
    # to chose relevant offer from given ones
    selected_offer_index = 0 # I am selecting first offer
    operator = "SOGP"  # quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["operator"]["code"]
    service = "RelaisColis" # quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["service"]["code"]

    packages = [{"type": "colis", "poids": 3, "longueur": 7, "largeur": 8, "hauteur":11, "description": "Newspapers"},
                {"type": "pli", "poids": 10, "longueur": 6, "largeur": 8, "description": "Cloth"}]
    package_type_value_in_euros = {"colis": 10, "pli": 8} # Save the different package type value in euros
    order_info = {
        "platform": platform,
        "expediteur.type": sender_type, "expediteur.pays": sender_country_code, "expediteur.code_postal": sender_postal_code,
        "expediteur.ville": sender_city, "expediteur.adresse": sender_address,  "expediteur.civilite": sender_title,
        "expediteur.prenom": sender_name, "expediteur.nom": sender_surname, "expediteur.email": sender_email,
        "expediteur.tel": sender_tel, "expediteur.infos": sender_address_additional_info,
        "destinataire.type": receiver_type, "destinataire.pays": receiver_country_code, "destinataire.code_postal": receiver_postal_code,
        "destinataire.ville": receiver_city, "destinataire.adresse": receiver_address,  "destinataire.civilite": receiver_title,
        "destinataire.prenom": receiver_name, "destinataire.nom": receiver_surname, "destinataire.email": receiver_email,
        "destinataire.tel": receiver_tel, "destinataire.infos": receiver_address_additional_info,
        "code_contenu": content_code, "collecte": collection_date, "delai": delay, "service": service, "operateur": operator}
    # Block for Optional Parameter in Order
    if True:
        pickup_availability_time = "09:00" # Time in HH:MM format (24 hours format)
        delivery_availability_time = "19:00" # Time in HH:MM format (24 hours format)
        final_date_of_delivery = "25-07-2021" # Final date DD-MM-YYYY till package must be delivered.
        # Information to be selected from quotation API same service offer
        pickup_point_code = "SOGP-O1100" # list(filter(lambda x: x["code"] == "retrait.pointrelais", quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["mandatory_informations"]["parameter"])[0]["type"]["enum"]["value"][0]
        dropoff_point_code = "SOGP-O1177" # list(filter(lambda x: x["code"] == "depot.pointrelais", quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["mandatory_informations"]["parameter"])[0]["type"]["enum"]["value"][0]
        insurance = False # For insurance if True please Ref https://www.boxtal.com/fr/en/api for related parameters
        if insurance is False:
            order_info.update({"assurance.selected": "false"})
        order_info.update({"disponibilite.HDE": pickup_availability_time, "disponibilite.HLE": delivery_availability_time, "livraison_imperative.DIL": final_date_of_delivery, "retrait.pointrelais": pickup_point_code, "depot.pointrelais": dropoff_point_code})
    # Preparing the package parameters which are of type <type>_N.<poids/longueur/largeur/hauteur>
    order_info.update(create_package_param_dict(packages))
    for package_type, money_value in package_type_value_in_euros.items():
        order_info.update({'{}.valeur'.format(package_type): money_value})

    _, pickup_info = api.get_pickup_point_info(pickup_point_code)
    _, dropoff_info = api.get_dropoff_point_info(dropoff_point_code)

    _, order = api.create_order(order_info=order_info)
    # You should save the order object you get above for future reference purpose
    # Saving it in a order.json file here just for demo
    with open("order.json", "w") as f:
        f.write(json.dumps(order))
    order_reference = order.get("data", {}).get("order", {}).get("shipment", {}).get("reference", "")
    print("Reference:", order_reference)
    if order_reference:
        _, order_status = api.get_order_status(order_reference)