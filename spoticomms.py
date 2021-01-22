from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import spotipy.util as util
import pandas as pd
import random

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
    token = 'blank'
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


def filter_happy(songs, happysad, ratio):
    """Provide 'liked songs' dataframe, and 'happy', 'sad', or 'mixed' to have
    filtered songs returned"""
    to_sort = songs.copy()
    count = len(songs)
    if happysad == 'happy':
        happy_filtered = to_sort.sort_values(['valence'], ascending = False).head(int(count*ratio))
    if happysad == 'sad':
        happy_filtered = to_sort.sort_values(['valence']).head(int(count*ratio))
    if happysad == 'mixed':
        happy_filtered = to_sort.sort_values(['valence'])[int(count*ratio):count-(int(count*ratio))]
    return happy_filtered

def filter_acoustic(songs, acousticness, ratio):
    """Provide 'liked songs' dataframe, and 'acoustic', 'electronic', or 'both' to have
    filtered songs returned"""
    to_sort = songs.copy()
    count = len(songs)
    if acousticness == 'acoustic':
        acousticness_filtered = to_sort.sort_values(['acousticness'], ascending = False).head(int(count*ratio))
    if acousticness == 'electronic':
        acousticness_filtered = to_sort.sort_values(['acousticness']).head(int(count*ratio))
    if acousticness == 'both':
        acousticness_filtered = to_sort.sort_values(['acousticness'])[int(count*ratio):count-(int(count*ratio))]
    return acousticness_filtered

def filter_dancey(songs, dancerelax, ratio):
    """Provide 'liked songs' dataframe, and 'dance', 'relax', or 'both' to have
    filtered songs returned"""
    to_sort = songs.copy()
    count = len(songs)
    if dancerelax == 'dance':
        dancey_filtered = to_sort.sort_values(['danceability'], ascending = False).head(int(count*ratio))
    if dancerelax == 'relax':
        dancey_filtered = to_sort.sort_values(['danceability']).head(int(count*ratio))
    if dancerelax == 'both':
        dancey_filtered = to_sort.sort_values(['danceability'])[int(count*ratio):count-(int(count*ratio))]
    return dancey_filtered

def filter_vocals(songs, vocals, ratio):
    """Provide 'liked songs' dataframe, and 'vox', 'no vox', or 'both' to have
    filtered songs returned"""
    to_sort = songs.copy()
    count = len(songs)
    if vocals == 'no vox':
        vocals_filtered = to_sort.sort_values(['instrumentalness'], ascending = False).head(int(count*ratio))
    if vocals == 'vox':
        vocals_filtered = to_sort.sort_values(['instrumentalness']).head(int(count*ratio))
    if vocals == 'both':
        vocals_filtered = to_sort.sort_values(['instrumentalness'])[int(count*ratio):count-(int(count*ratio))]
    return vocals_filtered

def filter_songs(liked_songs, inputs, ratio):
    input1, input2, input3, input4 = inputs
    reference_songs = filter_happy(liked_songs, input1, ratio)
    reference_songs = filter_acoustic(reference_songs, input2, ratio)
    reference_songs = filter_dancey(reference_songs, input3, ratio)
    reference_songs = filter_vocals(reference_songs, input4, ratio)
    print(len(reference_songs))
    return reference_songs

def descriptions(inputs):
    input1, input2, input3, input4 = inputs
    input1_dict = {'happy':'happy playlist', 'sad':'sad playlist', 'mixed':'playlist with mixed emotions'}
    input2_dict = {'acoustic':'mostly acoustic','electronic':'mostly electronic', 'both':'both acoustic and electronic'}
    input3_dict = {'dance':'dancey vibes', 'relax':'relaxed vibes', 'both':'vibes somewhere between dancey and relaxed'}
    input4_dict = {'vox':'lots of vocals', 'no vox':'hopefully no vocals', 'both':'some vocals here and there'}
    attributes = input1_dict[input1], input2_dict[input2], input3_dict[input3], input4_dict[input4]
    return attributes

def retrieve_recs(references, sp, inputs):

    song_uris = [uri for uri in references['URI']]
    if len(song_uris) > 5:
        song_uris = random.sample(song_uris, 5)

    print(song_uris)

    recs = sp.recommendations(seed_artists=[], seed_tracks=song_uris, seed_genres=[], limit=100)

    # converting recs into list of track uris
    recs_tracks = []
    for item in recs['tracks']:
        recs_tracks.append(item['uri'])

    #adding features data to recs
#    features = []
#    for track in recs_tracks:
#        song_features = sp.audio_features(tracks=track)
#        features.extend(song_features)

#    features = pd.DataFrame(features)
#    recs_tracks = pd.DataFrame(recs_tracks)
#    recs = recs_tracks.join(features)

    #filtering recs based on input choices
#    filtered_recs = filter_songs(recs, inputs, ratio=.75)

    # testing creating the new playlist
    user = sp.me()['display_name']

    playlist_name = 'Discovery²2'

    recs_details = sp.user_playlist_create(user, playlist_name, public=True, collaborative=False,
                                           description='Testing recommendation python script')
    playlist_id = recs_details['id']

    sp.user_playlist_add_tracks(user, playlist_id, recs_tracks, position=None)

    return user

def run(inputs):
    print(inputs)
    sp = login()
    library = pull_library_info(sp)
    references = filter_songs(library, inputs, ratio=1/3)
    user = retrieve_recs(references, sp, inputs)


