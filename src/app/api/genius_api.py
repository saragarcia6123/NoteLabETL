import asyncio
import re
from urllib.parse import urlencode
import aiohttp
import requests
from bs4 import BeautifulSoup
from src.server.api.api_handler import get_response

class GeniusAPI:
    def __init__(self, access_token, redirect_url):
        self._BASE_URL = 'https://api.genius.com'
        self._redirect_url = redirect_url
        self._access_token = access_token

    """Returns True if a valid access token is present"""
    async def authenticated(self):
        if self._access_token is None:
            return False
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url=f'{self._BASE_URL}/account',
                    headers=self._get_headers()
            ) as response:
                return response.status == 200

    def _get_headers(self):
        return {'Authorization': f'Bearer {self._access_token}'}

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
        if await self.authenticated():
            print('Already authenticated')
            return self._access_token
        response = await self._exchange_oauth_code(code, client_id, client_secret)
        self._access_token = response['access_token']
        print("Generated Access Token")
        return self._access_token

    async def _exchange_oauth_code(self, code, client_id, client_secret):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f'{self._BASE_URL}/oauth/token',
                data={
                    'code': code,
                    'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': self._redirect_url,
                    'response_type': 'code',
                    'grant_type': 'authorization_code',
                }
            ) as response:
                response.raise_for_status()
                return await response.json()

    """Returns the matching Genius songs according to Song and Artist"""
    async def get_songs_data(self, songs, artists, retries, delay):
        async with aiohttp.ClientSession() as session:
            tasks = [
            get_response(
                base_url=self._BASE_URL,
                endpoint='/search',
                headers=self._get_headers(),
                params={'q': f'{song} {artist}'},
                session=session,
                retries=retries,
                delay=delay
            ) for song, artist in zip(songs, artists)]
            results = await asyncio.gather(*tasks)
        return [result.get('response', {}).get('hits', []) for result in results]

    @staticmethod
    def scrape_lyrics(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        lyrics_div = soup.find('div', class_=re.compile(r'^Lyrics__Container'))
        if lyrics_div:
            text = lyrics_div.get_text("\n", strip=True)
            text = ' '.join(text.splitlines())
            return re.sub(r'\[.*?]', ' ', text)
        return "Lyrics not found"

