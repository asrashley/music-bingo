"""
Options for setting privacy policy
"""

from typing import Any, Dict, List

from .extra import ExtraOptions
from .option_field import OptionField

class PrivacyOptions(ExtraOptions):
    """
    Options for setting privacy policy
    """
    DESCRIPTION = "Privacy policy options"
    SHORT_PREFIX = "privacy"
    LONG_PREFIX = "privacy"

    OPTIONS: List[OptionField] = [
        OptionField('name', str, 'Company Name', '', None, None, None),
        OptionField('email', str, 'Company Email', '', None, None, None),
        OptionField('address', str, 'Company Address', '', None, None, None),
        OptionField('data_center', str, 'Data Center', '', None, None, None),
        OptionField('ico', str, 'Information Commissioner URL', '', None, None, None),
    ]

    def __init__(self,
                 privacy_name: str = "",
                 privacy_email: str = "",
                 privacy_address: str = "",
                 privacy_data_center: str = '',
                 privacy_ico: str = "",
                 **_,
                 ):
        self.name = privacy_name
        self.email = privacy_email
        self.address = privacy_address
        self.data_center = privacy_data_center
        self.ico = privacy_ico
        self.load_environment_settings()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert options to a dictionary
        """
        retval = {}
        for key, value in self.__dict__.items():
            if key[0] == '_':
                continue
            retval[key] = value
        return retval

    def update(self, **kwargs) -> bool:
        changed = False
        for key, value in kwargs.items():
            if key in self.__dict__ and getattr(self, key) != value:
                changed = True
                setattr(self, key, value)
        return changed
