"""
Enumeration for group types
"""
import enum


class Group(enum.IntFlag):
    """
    Enumeration for group types
    """
    USERS = 0x00000001
    CREATORS = 0x00000002
    HOSTS = 0x00000004
    GUESTS = 0x00000008
    ADMIN = 0x40000000
