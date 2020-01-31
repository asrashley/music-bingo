"""Various exceptions that can be raised by the MP3 engine"""

class NotAnMP3Exception(Exception):
    """Exception raised when checking a file that's not an MP3 file"""

class InvalidMP3Exception(Exception):
    """Exception raised for an MP3 file that can't be used"""
