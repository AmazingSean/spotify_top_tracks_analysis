import pandas as pd
import numpy as np
import sys
import spotipy
import spotipy.util as util


def get_features_with_id(id, sp):
    """
        Get audio features provided by Spotify Web API.
    """

    track = sp.audio_features(id)[0]
    feature_values = [track[feature] for feature in feature_names]

    return feature_values

def get_features_from_audio_analysis(id, sp):
    """
        Construct new features from the audio analysis provided by Spotify Web API.
    """
    analysis = sp.audio_analysis(id)

    # analysis is a dictionary that has keys: meta(irrelevant info), track, bars, beats, tatums, sections, segments
    track = analysis['track']
    bars = analysis['bars']
    beats = analysis['beats']
    tatums = analysis['tatums']
    sections = analysis['sections']
    segments = analysis['segments']

    # construct new features:
    tempo_confidence = track['tempo_confidence']
    time_signature_confidence = track['time_signature_confidence']
    key_confidence = track['key_confidence']
    mode_confidence = track['mode_confidence']

    num_bars = len(bars)

    num_beats = len(beats)

    num_tatums = len(tatums)

    num_sections = len(sections)

    num_segments = len(segments)

    result_list = [tempo_confidence, time_signature_confidence, key_confidence, mode_confidence,
                    num_bars, num_beats, num_tatums, num_sections, num_segments]

    return result_list


if __name__ == '__main__':
    # construct spotify object
    scope = 'user-library-read'
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print ("Usage: %s username" % (sys.argv[0],))
        sys.exit()
        
    token = util.prompt_for_user_token(username,scope,client_id='ff9ff248e80e428bbb9796e1a7d62aeb',
                                   client_secret='7f70a7c884494c6c96d2e6f03c4d2388', redirect_uri='http://localhost/')
    
    sp = spotipy.Spotify(auth=token)


    sample = pd.read_csv('sample.csv')

    # list of features 1. provided by Spotify 2. newly constructed features from audio analysis:
    feature_names = ['duration_ms', 'key', 'mode', 'time_signature', 'acousticness', 'danceability', 
                'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo']
    
    # expand the df to fit the new features:
    column_names = list(sample.columns)
    column_names.extend(feature_names)
    sample = sample.reindex(columns = column_names)

    # assign the new features
    sample[feature_names] = sample['Spotify_Track_ID'].apply(lambda x: pd.Series(get_features_with_id(x, sp)))


    # construct features from audio analysis:
    new_feature_names = ['tempo_confidence', 'time_signature_confidence', 'key_confidence', 'mode_confidence',
                        'num_bars', 'num_beats', 'num_tatums', 'num_sections', 'num_segments']

    # expand the df
    column_names.extend(new_feature_names)
    sample = sample.reindex(columns = column_names)
    
    # assign the new features:
    sample[new_feature_names] = sample['Spotify_Track_ID'].apply(lambda x: pd.Series(get_features_from_audio_analysis(x, sp)))

    print(sample.head())