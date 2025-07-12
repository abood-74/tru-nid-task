from rest_framework.throttling import UserRateThrottle

class EgyptianIDThrottle(UserRateThrottle):
    rate = '1000/hour'