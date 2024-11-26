import json
import time
import asyncio
import aiohttp
from urllib.parse import urlencode
import requests

class SpotifyAPI:

    def __init__(self, access_token, token_expires):
        self._BASE_URL = 'https://api.spotify.com/v1'
        self._access_token = access_token
        self._token_expires = token_expires
    
    def _get_headers(self):

        if not self._access_token or time.time() >= self._token_expires:
            self._generate_access_token()
        
        return {'Authorization': f'Bearer {self._access_token}'}

    def _generate_access_token(self):
        
        with open(self._secrets_path) as f:
            secrets = json.load(f)
        
        CLIENT_ID = secrets['SPOTIFY_CLIENT_ID']
        CLIENT_SECRET = secrets['SPOTIFY_CLIENT_SECRET']

        auth_url = 'https://accounts.spotify.com/api/token'
        
        response = requests.post(auth_url, {
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        })
        
        token_data = response.json()
            
        self._access_token = token_data['access_token']
        self._token_expires = time.time() + token_data['expires_in']
        
        print("Generated Access Token")

    """Returns the json data of the first matching track according to Song and Artist"""
    async def get_matching_track(self, song, artist, session, retries, delay):
    
        params = {
            'q': f'track:{song} artist:{artist}',
            'type': 'track',
            'limit': 1
        }

        endpoint = '/search'
    
        data = await self._get_response(params, endpoint, session, retries, delay)
        match = data.get('tracks', {}).get('items', []) if data else None
                
        return match[0] if match else None

    """Returns the matching Spotify Track URIs of tracks according to their Song and Artist"""
    async def get_matching_tracks_uris(self, songs, artists, retries, delay):
        
        async with aiohttp.ClientSession() as session:
            
            tasks = [self.get_matching_track(song, artist, session, retries, delay) for song, artist in zip(songs, artists)]
            matches = await asyncio.gather(*tasks)
            uris = [track['uri'] if track else None for track in matches]
            
        return uris

    """Returns the json track data from a list of track ids"""
    async def get_tracks_data(self, track_ids, retries, delay):
        
        async with aiohttp.ClientSession() as session:
            
            tasks = [self._get_tracks_data(track_ids[i:i+50], session, retries, delay) for i in range(0, len(track_ids), 50)]
            results = await asyncio.gather(*tasks)
            
        tracks = [track for result in results for track in result['tracks']]
        return tracks

    async def _get_tracks_data(self, track_ids, session, retries, delay):

        params = {
            'ids': ','.join(track_ids),
            'market': 'US'
        }
        
        endpoint = '/tracks'

        data = await self._get_response(params, endpoint, session, retries, delay)
   
        return data

    """Returns the json artists data from a list of artist ids"""
    async def get_artists_data(self, artist_ids, retries, delay):
        
        async with aiohttp.ClientSession() as session:
            
            tasks = [self._get_artists_data(artist_ids[i:i+50], session, retries, delay) for i in range(0, len(artist_ids), 50)]
            results = await asyncio.gather(*tasks)
            
        artists = [artist for result in results for artist in result['artists']]
        return artists

    async def _get_artists_data(self, artist_ids, session, retries, delay):

        params = {
            'ids': ','.join(artist_ids),
        }
        
        endpoint = '/artists'

        data = await self._get_response(params, endpoint, session, retries, delay)
   
        return data

    """Returns the json artists data from a list of artist ids"""
    async def get_albums_data(self, album_ids, retries, delay):
        
        async with aiohttp.ClientSession() as session:
            
            tasks = [self._get_albums_data(album_ids[i:i+20], session, retries, delay) for i in range(0, len(album_ids), 20)]
            results = await asyncio.gather(*tasks)
            
        albums = [album for result in results for album in result['albums']]
        return albums

    async def _get_albums_data(self, album_ids, session, retries, delay):

        params = {
            'ids': ','.join(album_ids),
        }
        
        endpoint = '/albums'

        data = await self._get_response(params, endpoint, session, retries, delay)
   
        return data

    async def get_tracks_audio_features(self, track_ids, retries, delay):
        
        async with aiohttp.ClientSession() as session:
            
            tasks = [self._get_tracks_audio_features(track_ids[i:i+50], session, retries, delay) for i in range(0, len(track_ids), 50)]
            results = await asyncio.gather(*tasks)

        tracks = [track for result in results for track in result['audio_features']]
        return tracks

    async def _get_tracks_audio_features(self, track_ids, session, retries, delay):

        params = {
            'ids': ','.join(track_ids)
        }
        
        endpoint = '/audio-features'

        data = await self._get_response(params, endpoint, session, retries, delay)
   
        return data

    async def get_tracks_audio_analysis(self, track_ids, retries, delay):
        
        async with aiohttp.ClientSession() as session:
            
            tasks = [self._get_track_audio_analysis(track_id, session, retries, delay) for track_id in track_ids]
            tracks = await asyncio.gather(*tasks)
            
        return tracks

    async def _get_track_audio_analysis(self, track_id, session, retries, delay):

        params = {}
        endpoint = f'/audio-analysis/{track_id}'

        data = await self._get_response(params, endpoint, session, retries, delay)
   
        return data

    """Handles asynchronous requests to server and returns the response json"""
    async def _get_response(self, params, endpoint, session, retries, delay):

        url = f"{self._BASE_URL}{endpoint}?{urlencode(params)}"

        headers=self._get_headers()
    
        data = None
        attempts = 0
        retriable_statuses = {429, 500, 503, 504}
        
        while data is None and attempts < retries:
            attempts += 1
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status in retriable_statuses:
                        await asyncio.sleep(delay)
                        continue
                    elif response.status == 401:
                        self._generate_access_token()
                        headers = self._get_headers()
                        continue
                    else:
                        response.raise_for_status()
                    
                    data = await response.json()
            except Exception as e:
                print(f"Error fetching data: {e}")
                if attempts >= retries:
                    raise
                await asyncio.sleep(delay)
   
        return data
 