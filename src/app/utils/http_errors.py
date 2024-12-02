"""
This class contains custom error classes for use in HTTP requests.
It is currently used for external async requests to handle retries and authentication
"""

class InvalidAccessTokenError(Exception):
    """Exception raised when a 401 error occurs and the access token is expired or invalid."""
    def __init__(self, message="Access token expired or invalid. Please re-authenticate."):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(Exception):
    """Exception raised when access is forbidden (403)."""
    def __init__(self, message="Access forbidden. You do not have the required permissions."):
        self.message = message
        super().__init__(self.message)


class ResourceNotFoundError(Exception):
    """Exception raised when a requested resource is not found (404)."""
    def __init__(self, message="The requested resource was not found."):
        self.message = message
        super().__init__(self.message)


class RateLimitExceededError(Exception):
    """Exception raised when the API rate limit is exceeded (429)."""
    def __init__(self, message="Rate limit exceeded. Slow down and try again later."):
        self.message = message
        super().__init__(self.message)


class InternalServerError(Exception):
    """Exception raised when the server encounters an internal error (500)."""
    def __init__(self, message="Internal server error. Try again later."):
        self.message = message
        super().__init__(self.message)


class ServiceUnavailableError(Exception):
    """Exception raised when the server is unavailable (503)."""
    def __init__(self, message="Service unavailable. Try again later."):
        self.message = message
        super().__init__(self.message)


class GatewayTimeoutError(Exception):
    """Exception raised when the server times out (504)."""
    def __init__(self, message="Gateway timeout. The server took too long to respond."):
        self.message = message
        super().__init__(self.message)


class MaximumRetriesError(Exception):
    """Exception raised when the maximum number of retries is exceeded."""
    def __init__(self, status_code, message="Maximum retries exceeded."):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Status Code: {self.status_code} - {self.message}")


class RequestFailedError(Exception):
    """Exception raised for any other general request failure."""
    def __init__(self, status_code, message="Request failed. Check your request or try again."):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Status Code: {self.status_code} - {self.message}")

ERROR_MAP = {
    401: InvalidAccessTokenError,
    403: ForbiddenError,
    404: ResourceNotFoundError,
    429: RateLimitExceededError,
    500: InternalServerError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}

RETRYABLE_EXCEPTIONS =  {
    RateLimitExceededError,
    InternalServerError,
    GatewayTimeoutError,
    ServiceUnavailableError,
    RequestFailedError
}
