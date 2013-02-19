from .patches import patch


def initialize(context):
    """Zope product initilisation code.
    """
    patch()
