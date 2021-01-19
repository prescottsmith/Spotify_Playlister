from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import spotipy.util as util
import pandas as pd

def login():
    # Define app access credentials
    CID = '6edd75f2e0c5465a98ef5b9a6678f54e'
    SECRET = '814350f64e5241959bd1f5d94c9854bf'
    username = ''

    #REDIRECT = 'https://developer.spotify.com/discover/'
    REDIRECT = 'http://localhost:8051/'
    # Defining scope of app access
    scope = "user-library-read playlist-modify-public playlist-read-private"

    # Connecting to spotify web API
    client_credentials_manager = SpotifyClientCredentials(client_id=CID, client_secret=SECRET)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    token = util.prompt_for_user_token(username, scope, CID, SECRET, REDIRECT)

    if token:
        sp = spotipy.Spotify(auth=token)
    else:
        print("Can't get token for", username)

    return sp

def pull_library_info(sp):
    # Pulling all liked songs
    offset = 0
    library = []
    liked = sp.current_user_saved_tracks(limit=50, offset=offset)

    while len(liked['items']) > 0:
        library.extend(liked['items'])
        offset = offset + 50
        liked = sp.current_user_saved_tracks(limit=50, offset=offset)

    # Converting library to dataframe
    liked_songs = []

    for song in library:
        info = song['track']
        df_row = {'Track': info['name'], 'Artist': [artist['name'] for artist in info['artists']],
                  'URI': info['uri'], 'Popularity': info['popularity']}
        liked_songs.append(df_row)

    liked_songs = pd.DataFrame(liked_songs)

    # Adding audio features
    song_uris = list(liked_songs['URI'])
    repeats = len(song_uris) // 100

    features = []
    for i in range(0, repeats + 1):
        uris = song_uris[0 + 100 * i:100 + 100 * i]
        song_features = sp.audio_features(tracks=uris)
        features.extend(song_features)

    features = pd.DataFrame(features)
    liked_songs = liked_songs.join(features)

    # Gives us useable dataframe to filter out results to feed recommender

    return liked_songs


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
    if acousticness == 'both':
        acousticness_filtered = songs[songs['acousticness'] < .66]
        acousticness_filtered = acousticness_filtered[acousticness_filtered['acousticness'] > .33]
    return acousticness_filtered
def filter_dancey(songs, dancerelax):
    """Provide 'liked songs' dataframe, and 'happy', 'sad', or 'mixed' to have
    filtered songs returned"""
    if dancerelax == 'dance':
        dancey_filtered = songs[songs['danceability'] >.66]
    if dancerelax == 'relax':
        dancey_filtered = songs[songs['danceability'] < .33]
    if dancerelax == 'mixed':
        dancey_filtered = songs[songs['danceability'] < .66]
        dancey_filtered = dancey_filtered[dancey_filtered['valence'] > .33]
    return dancey_filtered

def filter_vocals(songs, vocals):
    """Provide 'liked songs' dataframe, and 'happy', 'sad', or 'mixed' to have
    filtered songs returned"""
    if vocals == 'no vox':
        vocals_filtered = songs[songs['instrumentalness'] >.66]
    if vocals == 'vox':
        vocals_filtered = songs[songs['instrumentalness'] < .33]
    if vocals == 'both':
        vocals_filtered = songs[songs['instrumentalness'] < .66]
        vocals_filtered = vocals_filtered[vocals_filtered['valence'] > .33]
    return vocals_filtered

def filter_songs(liked_songs, inputs):
    input1, input2, input3, input4 = inputs
    reference_songs = filter_happy(liked_songs, input1)
    reference_songs = filter_acoustic(reference_songs, input2)
    reference_songs = filter_dancey(reference_songs, input3)
    reference_songs = filter_vocals(reference_songs, input4)
    return reference_songs

def retrieve_recs(references, sp):

    song_uris = [uri for uri in references['URI']]
    song_uris = song_uris[0:4]
    print(song_uris)

    recs = sp.recommendations(seed_artists=[], seed_tracks=song_uris, seed_genres=[], limit=30)

    # converting recs into list of track uris
    recs_tracks = []
    for item in recs['tracks']:
        recs_tracks.append(item['uri'])

    # testing creating the new playlist
    user = sp.me()['display_name']

    playlist_name = 'Discovery²'

    recs_details = sp.user_playlist_create(user, playlist_name, public=True, collaborative=False,
                                           description='Testing recommendation python script')
    playlist_id = recs_details['id']

    sp.user_playlist_add_tracks(user, playlist_id, recs_tracks, position=None)

    return user

def run(inputs):
    print(inputs)
    sp = login()
    library = pull_library_info(sp)
    references = filter_songs(library, inputs)
    user = retrieve_recs(references, sp)


