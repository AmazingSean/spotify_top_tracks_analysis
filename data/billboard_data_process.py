import pandas as pd
import numpy as np
import sys

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials

from pandarallel import pandarallel


def get_features_with_id(id, sp):
    """
        Get audio features provided by Spotify Web API.
    """
    print(id)

    track = sp.audio_features(id)[0]
    feature_values = [track[feature] for feature in feature_names]

    return feature_values

def get_unique_track_keys(sections):
    unique_keys_list = np.unique([str(section['key']) for section in sections])
    return ','.join(unique_keys_list)

def get_unique_track_modes(sections):
    unique_modes_list = np.unique([str(section['mode']) for section in sections])
    return ','.join(unique_modes_list)

def get_unique_track_modes(sections):
    unique_time_list = np.unique([str(section['time_signature']) for section in sections])
    return ','.join(unique_time_list)


def get_features_from_audio_analysis(id, sp):
    """
        Construct new features from the audio analysis provided by Spotify Web API.
    """
    print(id)
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

    #bars
    num_bars = len(bars)
    avg_bar_len = np.mean([bar['duration'] for bar in bars])
    avg_bar_conf = np.mean([bar['confidence'] for bar in bars])
    
    #beats
    num_beats = len(beats)
    avg_beat_len = np.mean([beat['duration'] for beat in beats])
    avg_beat_conf = np.mean([beat['confidence'] for beat in beats])

    #tatums
    num_tatums = len(tatums)
    avg_tatum_len = np.mean([tatum['duration'] for tatum in tatums])
    avg_tatum_conf = np.mean([tatum['confidence'] for tatum in tatums])

    #sections
    num_sections = len(sections)
    avg_section_len = np.mean([section['duration'] for section in sections])
    avg_tempo = np.mean([section['tempo'] for section in sections])
    avg_tempo_conf = np.mean([section['tempo_confidence'] for section in sections])
    key = get_unique_track_keys(sections)
    avg_key_conf = np.mean([section['key_confidence'] for section in sections])
    mode = get_unique_track_modes(sections)
    avg_mode_conf = np.mean([section['mode_confidence'] for section in sections])
    time_signature = get_unique_time_signatures(sections)
    avg_time_conf = np.mean([section['time_signature_confidence'] for section in sections])

    #segments
    num_segments = len(segments)


    result_list = [tempo_confidence, time_signature_confidence, key_confidence, mode_confidence,
                    num_bars, num_beats, num_tatums, num_sections, num_segments, avg_bar_len,
                    avg_bar_conf, avg_beat_len, avg_bar_conf, avg_tatum_len, avg_tatum_conf,
                    avg_section_len, avg_tempo, avg_tempo_conf, key, avg_key_conf, mode, 
                    avg_mode_conf, time_signature, avg_time_conf
                    ]

    return result_list


if __name__ == '__main__':
    # construct spotify object
    
    client_credentials_manager = SpotifyClientCredentials(client_id='ff9ff248e80e428bbb9796e1a7d62aeb', client_secret='7f70a7c884494c6c96d2e6f03c4d2388')
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    pandarallel.initialize(progress_bar=True)

    billboard = pd.read_csv('billboard_with_ids.csv')

    # list of features 1. provided by Spotify 2. newly constructed features from audio analysis:
    feature_names = ['duration_ms', 'key', 'mode', 'time_signature', 'acousticness', 'danceability', 
                'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo']
    
    # expand the df to fit the new features:
    column_names = list(billboard.columns)
    column_names.extend(feature_names)
    billboard = billboard.reindex(columns = column_names)

    # assign the new features
    print('Adding features...')
    billboard[feature_names] = billboard['sp_id'].apply(lambda x: pd.Series(get_features_with_id(x, sp)))


    # construct features from audio analysis:
    new_feature_names = ['tempo_confidence', 'time_signature_confidence', 'key_confidence', 'mode_confidence',
                        'num_bars', 'num_beats', 'num_tatums', 'num_sections', 'num_segments', 'avg_bar_len',
                        'avg_bar_conf', 'avg_beat_len', 'avg_bar_conf', 'avg_tatum_len', 'avg_tatum_conf',
                        'avg_section_len', 'avg_tempo', 'avg_tempo_conf', 'key', 'avg_key_conf', 'mode', 
                        'avg_mode_conf', 'time_signature', 'avg_time_conf']

    # expand the df
    column_names.extend(new_feature_names)
    billboard = billboard.reindex(columns = column_names)
    
    # assign the new features:
    print('Adding audio analysis...')
    billboard[new_feature_names] = billboard['sp_id'].apply(lambda x: pd.Series(get_features_from_audio_analysis(x, sp)))

    print(billboard.head())
    print('Saving to csv...')
    billboard.to_csv('billboard_with_features.csv')