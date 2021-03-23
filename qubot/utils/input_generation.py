from typing import Dict, Optional
from selenium.webdriver.firefox.webelement import FirefoxWebElement

def is_generatable_input(element: FirefoxWebElement):
    return element.tag_name == "textarea" or \
           (element.tag_name == "input" and element.get_attribute("type") in [
               "color",
               "date",
               "datetime-local",
               "email",
               "month",
               "number",
               "password",
               "search",
               "tel",
               "text",
               "time",
               "url",
               "week",
           ])

DEFAULT_COLOR = "#000000"
DEFAULT_DATE = "2021-01-01"
DEFAULT_DATETIME_LOCAL = "2021-01-01T01:00"
DEFAULT_EMAIL = "johndoe@gmail.com"
DEFAULT_MONTH = "2021-01"
DEFAULT_NUMBER = "1"
DEFAULT_PASSWORD = "p@ssw0rd"
DEFAULT_SEARCH = "query"
DEFAULT_TEL = "123-456-7890"
DEFAULT_TEXT = "text"
DEFAULT_TIME = "00:00:00.00"
DEFAULT_URL = "https://www.google.com/"
DEFAULT_WEEK = "2021-W01"

def generate_input(element: FirefoxWebElement, overrides: Dict[str, str] = None) -> Optional[str]:
    values = {
        "color": DEFAULT_COLOR,
        "date": DEFAULT_DATE,
        "datetime-local": DEFAULT_DATETIME_LOCAL,
        "email": DEFAULT_EMAIL,
        "month": DEFAULT_MONTH,
        "number": DEFAULT_NUMBER,
        "password": DEFAULT_PASSWORD,
        "search": DEFAULT_SEARCH,
        "tel": DEFAULT_TEL,
        "text": DEFAULT_TEXT,
        "time": DEFAULT_TIME,
        "url": DEFAULT_URL,
        "week": DEFAULT_WEEK,
    }

    if overrides:
        for input_type in overrides:
            values[input_type.lower()] = overrides[input_type]

    if not is_generatable_input(element):
        return None

    if element.tag_name == "textarea":
        return values["text"]

    return values[element.get_attribute("type").lower()]
