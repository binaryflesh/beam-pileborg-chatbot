#!/usr/bin/env python3.5
from .connection import Connection


def create(*args, **kwargs):
    """Helper function for the creation of connections."""
    return Connection(*args, **kwargs)
