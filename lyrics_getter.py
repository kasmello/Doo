import os
import random
import re
from lyricsgenius import Genius
from dotenv import load_dotenv


load_dotenv()
GENIUSKEY = os.getenv('GENIUS')

genius = Genius(GENIUSKEY)

def return_lyrics():

    songs = genius.artist_songs(630470, per_page=50, sort=random.choice(['popularity','title']))['songs']
    song = random.choice(songs)
    lyrics = genius.lyrics(song['id'])
    result = re.sub(r'^.*?({})\s'.format(re.escape(song['title'])), r'\1\n\n', lyrics, count=1)
    result = re.sub(r'(Lyrics)', r'\1\n\n', result, count=1)
    result = re.sub(r'\d+Embed$', '', result)
    result = re.sub(r'Embed', '', result)
    result = re.sub(r'See Joji Live', '', result)
    result = re.sub(r'Get tickets as low as \$\d+', '', result)
    result = re.sub(r'You might also like', '', result)
    return [result[i:i + 1600] for i in range(0, len(result), 1600)]

if __name__ == '__main__':
    return_lyrics()