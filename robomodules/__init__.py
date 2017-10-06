import os
from .server import Server

__path__.append(os.path.join(os.path.dirname(__file__), 'comm'))
__path__.append(os.path.join(os.path.dirname(__file__), 'messages'))

__all__ = ['Server']
