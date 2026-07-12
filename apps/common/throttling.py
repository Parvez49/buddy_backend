"""
Custom throttling classes for API rate limiting.
"""

from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Limit login attempts to prevent brute force attacks.
    Rate: 10 per minute
    """

    scope = "login"


class RegistrationRateThrottle(AnonRateThrottle):
    """
    Limit registration attempts to prevent spam.
    Rate: 5 per hour
    """

    scope = "registration"
    rate = "5/hour"
