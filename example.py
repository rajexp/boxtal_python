import json
from boxtal import BoxtalAPI
from constants import RunMode, ResponseFormat

# Set credentials below
USER_EMAIL = ""
USER_PASSWORD = ""
API_KEY = ""

if __name__ == '__main__':
    api = BoxtalAPI()
    api.set_mode(RunMode.TEST.value)
    api.set_credentials(USER_EMAIL, USER_PASSWORD, api_key=API_KEY)
    api.set_api_response_format(ResponseFormat.JSON)

    _, content_categories = api.get_content_categories() 
    _, content = api.get_all_content()

    # Example of quotation [ The search variables will be common for quotation and order API]
    # You can add multiple parcels below
    parcels = [{"type": "colis", "poids": 1, "longueur": 7, "largeur": 8, "hauteur":11, "value": 10.0, "description": "Newspapers"},
                {"type": "pli", "poids": 3, "longueur": 6, "largeur": 8, "value": 3.0, "description": "Cloth"}]
    from_ = BoxtalAPI.Sender(title = "Mr", name = "Nikola", surname = "Tesla", email = "nikola@gmail.com", tel = "0606060606", 
                country_code = "FR", postal_code = "44000", type = "particulier", company_name = "", city = "Paris", address = "Some address here")
    from_.address_additional_info = "" # To show that you can set property after object creation as well
    to = BoxtalAPI.Receiver(title = "Mr", name = "Jhon", surname = "Tesla", email = "jhon@gmail.com", tel = "0606060606",
                country_code = "FR", postal_code = "10036", type = "particulier", company_name ="", city = "New York", address = "Some address here",
                address_additional_info = "")

    delay = "aucun" # 'aucun', ‘minimum’ or ‘course’
    content_code = "10120"
    collection_date = "2021-07-25" # YYYY-MM-DD format
    operator = "UPSE"
    additional_parameters = {"code_contenu": content_code, "collecte": collection_date, "delai": delay, "operateur": operator}
    _, quotation = api.get_quotation(from_, to, parcels, additional_parameters)
    with open("quotation.json", "w") as f:
        f.write(json.dumps(quotation))
    _, countries = api.get_countries()

    # Example of order API and order status API
    # Information to be selected from quotation API offer
    # This need to be set according to selected offer or you may have some preference set of service operators to select from
    # to chose relevant offer from given ones
    selected_offer_index = 0 # I am selecting first offer
    operator = quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["operator"]["code"]
    service = quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["service"]["code"]

    additional_parameters = {"code_contenu": content_code, "collecte": collection_date, "delai": delay, "service": service, "operateur": operator}
    # Block for Optional Parameter in Order
    insurance = False # For insurance if True please Ref https://www.boxtal.com/fr/en/api for related parameters
    if insurance is False:
        additional_parameters.update({"assurance.selected": "false"})
    optional_param = True
    if optional_param:
        pickup_availability_time = "09:00" # Time in HH:MM format (24 hours format)
        delivery_availability_time = "19:00" # Time in HH:MM format (24 hours format)
        final_date_of_delivery = "28-07-2021" # Final date DD-MM-YYYY till parcels must be delivered.
        # Information to be selected from quotation API same service offer
        pickup_points_enum = list(filter(lambda x: x["code"] == "retrait.pointrelais", quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["mandatory_informations"]["parameter"]))[0].get("type", {})
        pickup_point_code = "" # Can be set based on enum availability
        dropoff_point_enum = list(filter(lambda x: x["code"] == "depot.pointrelais", quotation["data"]["cotation"]["shipment"]["offer"][selected_offer_index]["mandatory_informations"]["parameter"]))[0].get("type", {})
        dropoff_point_code = "" # Can be set based on enum availability
        additional_parameters.update({"disponibilite.HDE": pickup_availability_time, "disponibilite.HLE": delivery_availability_time, "livraison_imperative.DIL": final_date_of_delivery}) #, "retrait.pointrelais": pickup_point_code, "depot.pointrelais": dropoff_point_code})
    _, order = api.create_order(from_, to, parcels, additional_parameters)
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