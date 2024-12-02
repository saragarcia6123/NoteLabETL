"""
This class uses regex to format song and artist names for use in API search queries
"""

import re

def querify_song(song):
    song = song.lower()
    song = re.sub(r'\s*[(\[{].*?[)\]}]', '', song).rstrip()  # Remove content within brackets
    song = re.sub(r' - ', ' ', song)  # Replace ' - ' with a space
    song = re.sub(r'[;:/"]', '', song)  # Remove certain punctuation
    song = re.sub(r'[+|?!]|\.{3}', ' ', song)  # Replace special characters with a space
    return song.strip()  # Strip extra spaces
    
def querify_artist(artist):
    artist = artist.lower()  # Convert to lowercase
    artist = re.sub(r'\s*[(\[{].*?[)\]}]', '', artist).rstrip()  # Remove content within brackets
    artist = re.sub(r' - ', ' ', artist)  # Replace ' - ' with a space
    artist = re.split(r'\s*(feat|starring).*', artist)[0]  # Remove anything after "feat" or "starring"
    artist = re.sub(r'[+|?]|\.{3}', ' ', artist)  # Replace special characters with a space
    artist = re.sub(r'[¥:$&|/"]', '', artist)  # Remove additional unwanted characters
    artist = re.sub(r'\b(and|with|x|duet)\b', '', artist)  # Remove specific keywords
    return artist.strip()  # Strip extra spaces