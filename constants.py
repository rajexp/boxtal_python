from enum import Enum

class RunMode(Enum):
    TEST = "test"
    PROD = "prod"

class RequestType(Enum):
    GET = "GET"
    POST = "POST"

class ResponseFormat(Enum):
    XML = "XML"
    JSON = "JSON"