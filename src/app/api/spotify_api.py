import asyncio
import time
import aiohttp
import requests
from src.server.api.api_handler import get_response

class SpotifyAPI:
    def __init__(
            self,
            client_id,
            client_secret,
            access_token,
            token_expires,
        ):
        self._BASE_URL = 'https://api.spotify.com/v1'
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token = access_token
        self._token_expires = token_expires

    def set_access_token(self, access_token):
        self._access_token = access_token

    def set_token_expires(self, token_expires):
        self._token_expires = token_expires

    def set_client_id(self, client_id):
        self._client_id = client_id

    def set_client_secret(self, client_secret):
        self._client_secret = client_secret
    
    def _get_headers(self):
        if not self._access_token or time.time() >= self._token_expires:
            self.generate_access_token(self._client_id, self._client_secret)
        return {'Authorization': f'Bearer {self._access_token}'}

    def generate_access_token(self, client_id, client_secret):
        response = requests.post(
            url='https://accounts.spotify.com/api/token',
            data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
        })
        token_data = response.json()
        self._access_token, self._token_expires = token_data['access_token']
        self._token_expires = time.time() + token_data['expires_in']
        print("Generated Access Token")

    """Returns the matching Spotify Track URIs of tracks according to their Song and Artist"""
    async def get_matching_tracks_uris(self, songs, artists, limit, retries, delay):
        async with aiohttp.ClientSession() as session:
            tasks = [
                get_response(
                    base_url=self._BASE_URL,
                    endpoint='/search',
                    params={
                        'q': f'track:{song} artist:{artist}',
                        'type': 'track',
                        'limit': limit
                    },
                    headers=self._get_headers(),
                    session=session,
                    retries=retries,
                    delay=delay
                ) for song, artist in zip(songs, artists)]
            matches = await asyncio.gather(*tasks)
        return [result.get('tracks', {}).get('items', [])['uri'] if result else None for result in matches]

    """Returns the json track data from a list of track ids"""
    async def get_tracks_data(self, track_ids, retries, delay, batch_size=50):
        async with aiohttp.ClientSession() as session:
            tasks = [
                get_response(
                base_url=self._BASE_URL,
                endpoint='/tracks',
                params={'ids': ','.join(track_ids[i:i+batch_size])},
                headers=self._get_headers(),
                session=session,
                retries=retries,
                delay=delay
            ) for i in range(0, len(track_ids), batch_size)]
            results = await asyncio.gather(*tasks)
        return [track for result in results for track in result['tracks']]

    """Returns the json artists data from a list of artist ids"""
    async def get_artists_data(self, artist_ids, retries, delay, batch_size=50):
        async with aiohttp.ClientSession() as session:
            tasks = [
                get_response(
                    base_url=self._BASE_URL,
                    endpoint='/artists',
                    params={'ids': ','.join(artist_ids[i:i+batch_size])},
                    headers=self._get_headers(),
                    session=session,
                    retries=retries,
                    delay=delay
                ) for i in range(0, len(artist_ids), batch_size)
            ]
            results = await asyncio.gather(*tasks)
        return [artist for result in results for artist in result['artists']]

    """Returns the json artists data from a list of artist ids"""
    async def get_albums_data(self, album_ids, retries, delay, batch_size = 20):
        async with aiohttp.ClientSession() as session:
            tasks = [
                get_response(
                    base_url=self._BASE_URL,
                    endpoint='/albums',
                    params={'ids': ','.join(album_ids[i:i+batch_size])},
                    headers=self._get_headers(),
                    session=session,
                    retries=retries,
                    delay=delay
                ) for i in range(0, len(album_ids), batch_size)
            ]
            results = await asyncio.gather(*tasks)
        return [album for result in results for album in result['albums']]

    async def get_tracks_audio_features(self, track_ids, retries, delay, batch_size=50):
        async with aiohttp.ClientSession() as session:
            tasks = [
                get_response(
                    base_url=self._BASE_URL,
                    endpoint='/audio-features',
                    params={'ids': ','.join(track_ids[i:i+batch_size])},
                    headers=self._get_headers(),
                    session=session,
                    retries=retries,
                    delay=delay
                ) for i in range(0, len(track_ids), batch_size)
            ]
            results = await asyncio.gather(*tasks)
        return [track for result in results for track in result['audio_features']]

    async def get_tracks_audio_analysis(self, track_ids, retries, delay):
        async with aiohttp.ClientSession() as session:
            tasks = [
                get_response(
                    base_url=self._BASE_URL,
                    endpoint=f'/audio-analysis/{track_id}',
                    params={},
                    headers=self._get_headers(),
                    session=session,
                    retries=retries,
                    delay=delay
                ) for track_id in track_ids
            ]
            return await asyncio.gather(*tasks)

 