"""
API Blueprint initialization
"""
from flask import Blueprint


def create_api_blueprint():
    """Create and configure the API blueprint"""
    from . import routes
    return routes.api_bp