"""
Enumeration for group types
"""
import enum


class Group(enum.IntFlag):
    """
    Enumeration for group types
    """
    users = 0x00000001
    creator = 0x00000002
    host = 0x00000004
    guests = 0x00000008
    admin = 0x40000000
