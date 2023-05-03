"""
Options for sending emails
"""
from typing import List, Optional

from .extra import ExtraOptions
from .option_field import OptionField

class SmtpOptions(ExtraOptions):
    """
    Options for sending emails
    """
    DESCRIPTION = "Email server connection options"
    SHORT_PREFIX = "smtp"
    LONG_PREFIX = "smtp"
    OPTIONS: List[OptionField] = [
        OptionField('port', int, 'SMTP port', 25, 1, 65535, None),
        OptionField('server', str, 'server hostname', 'localhost', None, None, None),
        OptionField('sender', str, 'email address to use for sending',
                    None, None, None, None),
        OptionField('reply_to', str, 'email address to use as "reply to" address',
                    None, None, None, None),
        OptionField('username', str, 'username to use to authenticate',
                    None, None, None, None),
        OptionField('password', str, 'password to use to authenticate',
                    None, None, None, None),
        OptionField('starttls', bool, 'use STARTTLS rather than SSL',
                    None, None, None, None),
    ]

    def __init__(self,
                 smtp_port: int = 25,
                 smtp_server: str = 'localhost',
                 smtp_sender: Optional[str] = None,
                 smtp_reply_to: Optional[str] = None,
                 smtp_username: Optional[str] = None,
                 smtp_password: Optional[str] = None,
                 smtp_starttls: bool = False,
                 **_,
                 ):
        self.port = smtp_port
        self.server = smtp_server
        self.sender = smtp_sender
        self.reply_to = smtp_reply_to
        self.username = smtp_username
        self.password = smtp_password
        self.starttls = smtp_starttls
        self.load_environment_settings()

    def update(self, **kwargs) -> bool:
        changed = False
        for key, value in kwargs.items():
            if key in self.__dict__ and getattr(self, key) != value:
                changed = True
                setattr(self, key, value)
        return changed
