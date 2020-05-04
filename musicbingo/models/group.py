import enum

class Group(enum.IntFlag):
    users =   0x00000001
    creator = 0x00000002
    host =    0x00000004
    admin =   0x40000000
