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

    # Example of quotation
    # You can add multiple packages below
    packages = [{"type": "colis", "poids": 3, "longueur": 7, "largeur": 8, "hauteur":11},
                {"type": "pli", "poids": 10, "longueur": 6, "largeur": 8}]
    item_value_in_euros = 10
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
        "code_contenu": content_code, "type.valeur": item_value_in_euros,
        "expediteur.type": sender_type, "expediteur.pays": sender_country_code, "expediteur.code_postal": sender_postal_code,
        "destinataire.type": sender_type, "destinataire.pays": sender_country_code, "destinataire.code_postal": sender_postal_code,
        "collecte": collection_date, "delai": delay}
    # Preparing the package parameters which are of type <type>_N.<poids/longueur/largeur/hauteur>
    for index, package_info in enumerate(packages):
        package_prefix = '{}_{}'.format(package_info.get("type"), index+1)
        quotation_parameters.update({'{}.poids'.format(package_prefix): package_info['poids'], '{}.longueur'.format(package_prefix): package_info['longueur'],
            '{}.largeur'.format(package_prefix): package_info['largeur']})
        # Since hauteur is only applicable for package of type except pli
        if package_info["type"] != "pli":
            quotation_parameters.update({'{}.hauteur'.format(package_prefix): package_info['hauteur']})
    _, quotation = api.get_quotation(parameters=quotation_parameters)
