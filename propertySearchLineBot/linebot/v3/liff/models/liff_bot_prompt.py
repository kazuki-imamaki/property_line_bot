# coding: utf-8

"""
    LIFF server API

    LIFF Server API.  # noqa: E501

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""


import json
import pprint
import re  # noqa: F401
from aenum import Enum, no_arg





class LiffBotPrompt(str, Enum):
    """
    Specify the setting for bot link feature with one of the following values:  `normal`: Display the option to add the LINE Official Account as a friend in the channel consent screen. `aggressive`: Display a screen with the option to add the LINE Official Account as a friend after the channel consent screen. `none`: Don't display the option to add the LINE Official Account as a friend.   The default value is none. 
    """

    """
    allowed enum values
    """
    NORMAL = 'normal'
    AGGRESSIVE = 'aggressive'
    NONE = 'none'

    @classmethod
    def from_json(cls, json_str: str) -> LiffBotPrompt:
        """Create an instance of LiffBotPrompt from a JSON string"""
        return LiffBotPrompt(json.loads(json_str))


