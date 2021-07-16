from boxtal import BoxtalAPI
from constants import RunMode

# Set credentials below
USER_EMAIL = ""
USER_PASSWORD = ""
API_KEY = ""

if __name__ == '__main__':
    api = BoxtalAPI()
    api.set_mode(RunMode.TEST.value)
    api.set_credentials(USER_EMAIL, USER_PASSWORD, api_key=API_KEY)

    _, content_categories = api.get_content_categories() 
    _, content = api.get_all_content()
