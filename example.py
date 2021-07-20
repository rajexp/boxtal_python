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

    # Example of quotation [ The search variables will be common for quotation and order API]
    # You can add multiple packages below
    packages = [{"type": "colis", "poids": 1, "longueur": 7, "largeur": 8, "hauteur":11},
                {"type": "pli", "poids": 3, "longueur": 6, "largeur": 8}]
    package_type_value_in_euros = {"colis": 10.0, "pli": 8.0} # Save the different package type value in euros
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
    sender_email = "nikola@gmail.com"
    sender_tel = "0606060606"
    receiver_country_code = "FR"
    receiver_postal_code = "10036"
    receiver_type = "particulier" # ‘particulier’ or ‘entreprise’
    receiver_company_name ="" # Required if receiver_type is ‘entreprise’
    receiver_city = "New York"
    receiver_address = "Some address here"
    receiver_address_additional_info = ""
    receiver_title = "Mr"
    receiver_name = "Jhon"
    receiver_surname = "Tesla"
    receiver_email = "jhon@gmail.com"
    receiver_tel = "0606060606"
    delay = "aucun" # 'aucun', ‘minimum’ or ‘course’
    content_code = "10120"
    collection_date = "2021-07-21" # YYYY-MM-DD format

    quotation_parameters = {
        "code_contenu": content_code,
        "expediteur.type": sender_type, "expediteur.pays": sender_country_code, "expediteur.code_postal": sender_postal_code,
        "destinataire.type": receiver_type, "destinataire.pays": receiver_country_code, "destinataire.code_postal": receiver_postal_code,
        "collecte": collection_date, "delai": delay}
    # Preparing the package parameters which are of type <type>_N.<poids/longueur/largeur/hauteur>
    quotation_parameters.update(create_package_param_dict(packages))
    for package_type, money_value in package_type_value_in_euros.items():
        quotation_parameters.update({'{}.valeur'.format(package_type): money_value})
    _, quotation = api.get_quotation(parameters=quotation_parameters)
    with open("quotation.json", "w") as f:
        f.write(json.dumps(quotation))
    _, countries = api.get_countries()

    # Example of order API and order status API
    platform="api"
    platform_version = "1"
    # Information to be selected from quotation API offer
    # This need to be set according to selected offer or you may have some preference set of service operators to select from
    # to chose relevant offer from given ones
    selected_offer_index = 0 # I am selecting first offer
    # "CHRP"  #
    # "ChronoShoptoShop" #  
    operator = quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["operator"]["code"]
    service = quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["service"]["code"]

    packages = [{"type": "colis", "poids": 1, "longueur": 7, "largeur": 8, "hauteur":11, "description": "Newspapers"},
                {"type": "pli", "poids": 3, "longueur": 6, "largeur": 8, "description": "Cloth"}]
    package_type_value_in_euros = {"colis": 10, "pli": 8} # Save the different package type value in euros
    order_info = {
        "platform": platform, "platform_version": platform_version,
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
    insurance = False # For insurance if True please Ref https://www.boxtal.com/fr/en/api for related parameters
    if insurance is False:
        order_info.update({"assurance.selected": "false"})
    optional_param = True
    if optional_param:
        pickup_availability_time = "09:00" # Time in HH:MM format (24 hours format)
        delivery_availability_time = "19:00" # Time in HH:MM format (24 hours format)
        final_date_of_delivery = "25-07-2021" # Final date DD-MM-YYYY till package must be delivered.
        # Information to be selected from quotation API same service offer
        pickup_points_enum = list(filter(lambda x: x["code"] == "retrait.pointrelais", quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["mandatory_informations"]["parameter"]))[0].get("type", {})
        pickup_point_code = "" # Can be set based on enum availability
        dropoff_point_enum = list(filter(lambda x: x["code"] == "depot.pointrelais", quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["mandatory_informations"]["parameter"]))[0].get("type", {})
        dropoff_point_code = "" # Can be set based on enum availability
        order_info.update({"disponibilite.HDE": pickup_availability_time, "disponibilite.HLE": delivery_availability_time, "livraison_imperative.DIL": final_date_of_delivery}) #, "retrait.pointrelais": pickup_point_code, "depot.pointrelais": dropoff_point_code})
    # Preparing the package parameters which are of type <type>_N.<poids/longueur/largeur/hauteur>
    order_info.update(create_package_param_dict(packages))
    for package_type, money_value in package_type_value_in_euros.items():
        order_info.update({'{}.valeur'.format(package_type): money_value})
    _, order = api.create_order(order_info=order_info)
    # You should save the order object you get above for future reference purpose
    # Saving it in a order.json file here just for demo
    with open("order.json", "w") as f:
        f.write(json.dumps(order))
    order_reference = order.get("data", {}).get("order", {}).get("shipment", {}).get("reference", "")
    print("Reference:", order_reference)
    if order_reference:
        _, order_status = api.get_order_status(order_reference)
        print(order_status)

    if pickup_point_code:
        _, pickup_info = api.get_pickup_point_info(pickup_point_code)
        print(pickup_info)
    if dropoff_point_code:
        _, dropoff_info = api.get_dropoff_point_info(dropoff_point_code)
        print(dropoff_info)