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

    async def authenticate(self, code, client_id, client_secret):

        authenticated = await self.authenticated()
        
        if authenticated:
            print('Already authenticated')
            return self._access_token
    
        response = await self._exchange_auth_code(code, client_id, client_secret)
        print(response)
        self._access_token = response['access_token']
        
        print("Generated Access Token")
        return self._access_token

    async def _exchange_auth_code(self, code, client_id, client_secret):
        
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

    """Handles asynchronous requests to server and returns the response json"""
    async def _get_response(self, params, endpoint, session, retries, delay):

        url = f"{self._BASE_URL}{endpoint}?{urlencode(params)}"

        headers = self._get_headers()
    
        data = None
        attempts = 0
        retriable_statuses = {429, 500, 503, 504}
        
        while data is None and attempts < retries:
            attempts += 1
            async with session.get(url, headers=headers) as response:
                
                if response.status in retriable_statuses:
                    await asyncio.sleep(delay)
                    continue
                    
                elif response.status == 401:
                    self._generate_access_token()
                    headers = await self._get_headers()
                    continue
                    
                else:
                    response.raise_for_status()
                
                data = await response.json()
   
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