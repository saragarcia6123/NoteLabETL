import json
import time
import asyncio
import aiohttp
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
import re

class GeniusAPI:

    def __init__(self, access_token, redirect_url):
        self._BASE_URL = 'https://api.genius.com'
        self._redirect_url = redirect_url
        self._access_token = access_token

    """Returns True if a valid access token is present"""
    async def authenticated(self):

        if self._access_token is None:
            return False
        url = f'{self._BASE_URL}/account'
        headers = self._get_headers()

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return True
                else:
                    print(response.status)
                    return False

    def _get_headers(self):
        return {'Authorization': f'Bearer {self._access_token}'}

    def set_access_token(self, access_token):
        self._access_token = access_token

    def get_auth_url(self, state, client_id):

        params = {
            'client_id': client_id,
            'redirect_uri': self._redirect_url,
            'scope':'me create_annotation manage_annotation vote',
            'state': state,
            'response_type': 'code'
        }

        return f'{self._BASE_URL}/oauth/authorize?{urlencode(params)}'

    async def authenticate_oath(self, code, client_id, client_secret):

        authenticated = await self.authenticated()
        if authenticated:
            print('Already authenticated')
            return self._access_token

        response = await self._exchange_auth_code(code, client_id, client_secret)
        print(response)
        self._access_token = response['access_token']

        print("Generated Access Token")
        return self._access_token

    async def _exchange_oauth_code(self, code, client_id, client_secret):

        url = f'{self._BASE_URL}/oauth/token'

        params = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': self._redirect_url,
            'response_type': 'code',
            'grant_type': 'authorization_code',
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=params) as response:
                response.raise_for_status()
                return await response.json()

    """Returns the data of the first matching song"""
    async def _get_song_data(self, song, artist, session, retries, delay):

        params = {'q': f'{song} {artist}'}
        endpoint = '/search'
        data = await self._get_response(params, endpoint, session, retries, delay)
        hits = data.get('response', {}).get('hits', [])

        return hits[0] if hits else None

    """Returns the matching Genius song data of tracks according to their Song and Artist"""
    async def get_songs_data(self, songs, artists, retries, delay):

        async with aiohttp.ClientSession() as session:
            tasks = [self._get_song_data(song, artist, session, retries, delay) for song, artist in zip(songs, artists)]
            data = await asyncio.gather(*tasks)
        return data

    def get_lyrics(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        lyrics_div = soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-1 kUgSbL')
        if lyrics_div:
            text = lyrics_div.get_text("\n", strip=True)
            text = ' '.join(text.splitlines())
            return re.sub(r'\[.*?\]', ' ', text)

        return "Lyrics not found"

"""Handles asynchronous requests to server and returns the response json"""
async def _get_response(self, params, endpoint, session, retries, delay):
    url = f"{self._BASE_URL}{endpoint}?{urlencode(params)}"
    headers = self._get_headers()

    data = None
    attempts = 0

    while data is None and attempts < retries:
        attempts += 1
        async with session.get(url, headers=headers) as response:
            if response.status in self._ERROR_MAP:
                if response.status == 401 and not self._access_token:
                    exception = self.MissingTokenError()
                else:
                    exception = self._ERROR_MAP[response.status]()

                # Retry logic for retriable exceptions
                if isinstance(exception, tuple(self.retriable_exceptions)):
                    await asyncio.sleep(delay)
                    continue

                # Raise non-retryable exceptions immediately
                raise exception(f"Error {response.status}: {response.reason}")

            if not response.ok:
                raise self.RequestFailedError(response.status, f"Error {response.status}: {response.reason}")

            data = await response.json()

    # Raise a timeout error if no data after retries
    if data is None:
        raise self.RequestFailedError(
            status_code=504,
            message="Request timed out after maximum retries."
        )

    return data

    _ERROR_MAP = {
        401: TokenExpiredOrInvalidError,
        403: ForbiddenError,
        404: ResourceNotFoundError,
        429: RateLimitExceededError,
        500: InternalServerError,
        503: ServiceUnavailableError,
        504: GatewayTimeoutError,
    }

    retriable_exceptions =  {
        RateLimitExceededError,
        InternalServerError,
        GatewayTimeoutError,
        ServiceUnavailableError,
        RequestFailedError
    }

    class MissingTokenError(Exception):
        """Exception raised when a 401 error occurs and the token is missing."""
        def __init__(self, message="Access token is missing. Please provide a valid token."):
            self.message = message
            super().__init__(self.message)

    class TokenExpiredOrInvalidError(Exception):
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
            self.message = messageelse:  # Handle non-retryable errors

            super().__init__(self.message)

    class GatewayTimeoutError(Exception):
        """Exception raised when the server times out (504)."""
        def __init__(self, message="Gateway timeout. The server took too long to respond."):
            self.message = message
            super().__init__(self.message)

    class RequestFailedError(Exception):
        """Exception raised for any other general request failure."""
        def __init__(self, status_code, message="Request failed. Check your request or try again."):
            self.status_code = status_code
            self.message = message
            super().__init__(f"Status Code: {self.status_code} - {self.message}")
