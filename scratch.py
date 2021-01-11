from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import spotipy.util as util
import pandas as pd

#Define app access credentials
CID='6edd75f2e0c5465a98ef5b9a6678f54e'
SECRET='814350f64e5241959bd1f5d94c9854bf'
username = ''
user = 'prezzy318'

REDIRECT = 'https://soundcloud.com/costikyan'

#Defining scope of app access
scope = "user-library-read playlist-modify-public playlist-read-private"
    #to add more scopes, just include a space then the extra scope


#Connecting to spotify web API
client_credentials_manager = SpotifyClientCredentials(client_id=CID, client_secret=SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
token = util.prompt_for_user_token(username, scope, CID, SECRET, REDIRECT)

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)


#Pulling all liked songs
offset=0
library=[]
liked = sp.current_user_saved_tracks(limit=50, offset=offset)

while len(liked['items']) > 0:
    library.extend(liked['items'])
    offset=offset+50
    liked = sp.current_user_saved_tracks(limit=50, offset=offset)


#Converting library to dataframe
liked_songs = []

for song in library:
    info = song['track']
    df_row = {'Track':info['name'], 'Artist':[artist['name'] for artist in info['artists']],
              'URI':info['uri'], 'Popularity':info['popularity']}
    liked_songs.append(df_row)

liked_songs = pd.DataFrame(liked_songs)

#Adding audio features
song_uris = list(liked_songs['URI'])
repeats = len(song_uris)//100

features=[]
for i in range(0,repeats+1):
    uris = song_uris[0+100*i:100+100*i]
    song_features = sp.audio_features(tracks=uris)
    features.extend(song_features)

features = pd.DataFrame(features)
liked_songs = liked_songs.join(features)

#Gives us useable dataframe to filter out results to feed recommender


def filter_happy(songs, happysad):
    """Provide 'liked songs' dataframe, and 'happy', 'sad', or 'mixed' to have
    filtered songs returned"""
    if happysad == 'happy':
        happy_filtered = songs[songs['valence'] >.66]
    if happysad == 'sad':
        happy_filtered = songs[songs['valence'] < .33]
    if happysad == 'mixed':
        happy_filtered = songs[songs['valence'] < .66]
        happy_filtered = happy_filtered[happy_filtered['valence'] > .33]
    return happy_filtered


def filter_acoustic(songs, acousticness):
    """Provide 'liked songs' dataframe, and 'acoustic', 'electronic', or 'mixed' to have
    filtered songs returned"""
    if acousticness == 'acoustic':
        acousticness_filtered = songs[songs['acousticness'] >.66]
    if acousticness == 'electronic':
        acousticness_filtered = songs[songs['acousticness'] < .33]
    if acousticness == 'mixed':
        acousticness_filtered = songs[songs['acousticness'] < .66]
        acousticness_filtered = acousticness_filtered[acousticness_filtered['acousticness'] > .33]
    return acousticness_filtered



#test sourcing song data
test_songs = list(liked_songs['URI'])


song_features = sp.audio_features(tracks=test_songs) #this is only way to get extra info than what is returned in library call


album_uri = library[0]['track']['album']['uri']
album_info = sp.album(album_id = album_uri)
genre = album_info['genres']

songs_genre_list = []
for i in range(0,600):
    artist_uri = library[i]['track']['artists'][0]['uri']
    artist_info = sp.artist(artist_id=artist_uri)
    genre = artist_info['genres']
    songs_genre_list.append(genre)
    print(i)








#testing a recommendation
step_han_uri = library[3]['track']['uri']
dustpig_uri = library[12]['track']['uri']
manic_uri = library[78]['track']['uri']


rec_genre = ['deep-house', 'minimal-techno']
rec_songs = [step_han_uri, dustpig_uri, manic_uri]

recs = sp.recommendations(seed_artists=[], seed_tracks=rec_songs, seed_genres=rec_genre, limit=30)

#converting recs into list of track uris
recs_tracks=[]
for item in recs['tracks']:
    recs_tracks.append(item['uri'])

#testing creating the new playlist
recs_details = sp.user_playlist_create(user, 'Recs Test2', public=True, collaborative=False, description='Testing recommendation python script')
playlist_id = recs_details['id']

sp.user_playlist_add_tracks(user, playlist_id, recs_tracks, position=None)









