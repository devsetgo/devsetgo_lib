# -*- coding: utf-8 -*-
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from dsg_lib.endpoints.models import EmailVerification
from dsg_lib.endpoints.system_tools_endpoints import create_tool_router

# Create a FastAPI app for testing
app = FastAPI()
client = TestClient(app)
# Tools configuration
route_name = "/api"
config_tools = {"enable_email-validation": True}
tool_router = create_tool_router(config=config_tools)
app.include_router(tool_router, prefix=route_name, tags=["system-tools"])


def test_create_tool_router():
    config = {"enable_email-validation": True}
    router = create_tool_router(config)
    assert router is not None


@patch("dsg_lib.endpoints.system_tools_endpoints.validate_email_address")
def test_check_email(mock_validate_email_address):
    # Set up the mock function to return a valid response
    mock_validate_email_address.return_value = {
        "message": "Email validation successful",
        "information": {
            "normalized": "test@gmail.com",
            "valid": True,
            "local_part": "test",
            "domain": "gmail.com",
            "ascii_email": "test@gmail.com",
            "ascii_local_part": "test",
            "ascii_domain": "gmail.com",
            "smtputf8": False,
            "mx": None,
            "mx_fallback_type": None,
        },
        "dns_check": "https://dnschecker.org/all-dns-records-of-domain.php?query=gmail.com&rtype=ALL&dns=google",
        "error": False,
        "timer": None,
    }

    email_verification = EmailVerification(
        email_address="test@gmail.com",
        check_deliverability=True,
        test_environment=False,
    )
    response = client.post(
        f"{route_name}/email-validation", json=email_verification.dict()
    )
    if response.status_code != 200:
        print(response.text)
    assert response.status_code == 200
    assert "valid" in response.json()["information"]


# class Language(Enum):
#     """
#     Enumeration of supported languages with their human-readable names.
#     """

#     EN = "English"
#     # AM = "Amharic"
#     AR = "Arabic"
#     # AZ = "Azerbaijani"
#     BY = "Belarusian"
#     # CZ = "Czech"
#     DE = "German"
#     # DK = "Danish"
#     EN_GB = "English - Great Britain"
#     EN_IN = "English - India"
#     EN_NG = "English - Nigeria"
#     ES = "Spanish"
#     ES_CO = "Spanish - Colombia"
#     ES_VE = "Spanish - Venezuela"
#     ES_GT = "Spanish - Guatemala"
#     # FA = "Farsi"
#     FI = "Finnish"
#     FR = "French"
#     FR_CH = "French - Switzerland"
#     FR_BE = "French - Belgium"
#     FR_DZ = "French - Algeria"
#     HE = "Hebrew"
#     HU = "Hungarian"
#     ID = "Indonesian"
#     IS = "Icelandic"
#     IT = "Italian"
#     JA = "Japanese"
#     KN = "Kannada"
#     KO = "Korean"
#     KZ = "Kazakh"
#     LT = "Lithuanian"
#     LV = "Latvian"
#     NO = "Norwegian"
#     PL = "Polish"
#     PT = "Portuguese"
#     PT_BR = "Portuguese - Brazilian"
#     SL = "Slovene"
#     SR = "Serbian"
#     SV = "Swedish"
#     RO = "Romanian"
#     RU = "Russian"
#     TE = "Telugu"
#     TG = "Tajik"
#     TR = "Turkish"
#     TH = "Thai"
#     VI = "Vietnamese"
#     NL = "Dutch"
#     UK = "Ukrainian"


# class Currency(Enum):
#     """
#     Enumeration of supported currencies with their human-readable names.
#     """

#     USD = "US Dollar"
#     EUR = "Euro"
#     GBP = "British Pound"
#     AUD = "Australian Dollar"
#     BYN = "Belarusian Ruble"
#     CAD = "Canadian Dollar"
#     EEK = "Estonian Kroon"
#     LTL = "Lithuanian Litas"
#     LVL = "Latvian Lat"
#     RUB = "Russian Ruble"
#     SEK = "Swedish Krona"
#     NOK = "Norwegian Krone"
#     PLN = "Polish Zloty"
#     MXN = "Mexican Peso"
#     RON = "Romanian Leu"
#     INR = "Indian Rupee"
#     HUF = "Hungarian Forint"
#     ISK = "Icelandic Krona"
#     UZS = "Uzbekistani Som"
#     SAR = "Saudi Riyal"


# class Message(BaseModel):
#     message: str


# class Configuration(BaseModel):
#     number: float
#     currency: str
#     language: str
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "number": 999999999999.99,
#                 "currency": "US Dollar",
#                 "language": "EN",
#             }
#         }
#     )


# class NumberWordsResponse(BaseModel):
#     words: str
#     configuration: Configuration
#     model_config = ConfigDict(
#         json_schema_extra={
#             "example": {
#                 "words": "nine hundred and ninety-nine billion, nine hundred and ninety-nine million, nine hundred and ninety-nine thousand, nine hundred and ninety-nine dollars, ninety-nine cents",
#                 "configuration": {
#                     "number": 999999999999.99,
#                     "currency": "US Dollar",
#                     "language": "EN",
#                 },
#             }
#         }
#     )


# @router.get("/currencies", response_model=List[str])
# def get_currencies():
#     """
#     Returns a list of all supported currencies along with their descriptions.
#     """
#     return [f"{currency.value}" for currency in Currency]


# @router.get("/languages", response_model=List[str])
# def get_languages():
#     """
#     Returns a list of all supported languages along with their descriptions.
#     """
#     return [f"{language.value}" for language in Language]


# @router.get(
#     "/number-words",
#     response_model=NumberWordsResponse,
#     responses={
#         400: {"model": Message},
#         422: {"model": Message},
#         500: {"model": Message},
#     },
# )
# async def number_to_words(
#     number: float = Query(12345678.90, le=999999999999.99, examples=[999999999999.99]),
#     currency: Currency = Currency.USD,
#     language: Language = Language.EN,
# ):
#     """
#     Endpoint to convert a numeric value to its word representation in a specified language and currency format.
#     The endpoint responds with a JSON object containing the word representation and the configuration used for conversion.
#     """
#     # Logging the details of the received request
#     logger.info(
#         f"Received request: number={number}, currency={currency.name}, language={language.name}"
#     )

#     try:
#         # Attempting to convert the number to words using the num2words library
#         words = num2words(
#             number, to="currency", lang=language.name.lower(), currency=currency.name
#         )
#         logger.info("Conversion successful")

#         # Returning the response in the specified format
#         return NumberWordsResponse(
#             words=words,
#             configuration=Configuration(
#                 number=number, currency=currency.value, language=language.value
#             ),
#         )
#     except Exception as e:
#         # Logging any errors that occur during the conversion
#         logger.error(f"Error in conversion: {str(e)}")

#         # Raising an HTTPException in case of an error
#         raise HTTPException(
#             status_code=500, detail="Error in converting number to words"
#         )
