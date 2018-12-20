#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (C) 2018 Eddie Antonio Santos <easantos@ualberta.ca>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Unit/Integration tests for views.
"""

import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest  # type: ignore
from django.shortcuts import reverse  # type: ignore
from django.test import Client  # type: ignore
from model_mommy import mommy  # type: ignore
from pydub import AudioSegment  # type: ignore


MAX_RECORDING_QUERY_TERMS = 3  # TODO: will this be a configuration option?


@pytest.mark.django_db
def test_serve_recording(client, exported_recording):
    """
    Test that a recording is served properly.
    """
    recording, file_contents = exported_recording
    page = client.get(reverse('validation:recording', kwargs={'recording_id': recording.id}))
    assert page.status_code == 200
    assert page.get('Content-Type') == 'audio/m4a'
    content = b''.join(page.streaming_content)
    assert content == file_contents
    assert content[4:12] == b'ftypM4A ', "Did not serve an .m4a file."

    # Make sure that caching is set up, and sufficiently aggressive.
    assert 'max-age=' in page.get('Cache-Control')
    assert 'public' in page.get('Cache-Control')
    assert 'must-revalidate' not in page.get('Cache-Control')
    # TODO: last modified date?
    assert page.get('ETag').startswith('"'), "Incorrect ETag syntax"
    assert page.get('ETag').endswith('"'), "Incorrect ETag syntax"
    assert page.get('ETag').strip('"') in recording.id, "The ETag should be based on the recording ID"


@pytest.mark.django_db
def test_search_recordings(client):
    # TODO: change this to ê-nipat when there is better database matching.
    phrase = mommy.make_recipe('validation.phrase', transcription='ênipat')
    speaker = mommy.make_recipe('validation.speaker')

    # Make two recordings. We want to make sure the query actually works by
    # only retrieving the *relevant* recording.
    recording = mommy.make_recipe('validation.recording', phrase=phrase, speaker=speaker)
    unrelated_recording = mommy.make_recipe('validation.recording')

    assert recording.phrase != unrelated_recording.phrase

    response = client.get(reverse('validation:search_recordings',
                                  kwargs={'query': 'ê-nipat'}))

    assert 'Access-Control-Allow-Origin' in response, "Missing requried CORS headers"

    recordings = response.json()
    assert isinstance(recordings, list)
    assert len(recordings) == 1
    recording = recordings[0]
    assert recording.get('wordform') == phrase.transcription
    # TODO: Change field name to "speaker_code"?
    assert 'speaker' in recording.keys()
    assert recording.get('gender') in 'MF'
    assert recording.get('recording_url').startswith(('http://', 'https://'))
    assert recording.get('recording_url').endswith('.m4a')
    assert recording.get('speaker_name') == speaker.full_name
    assert recording.get('anonymous') is False


@pytest.mark.django_db
def test_search_multiple_recordings(client):
    """
    Test for finding multiple recordings by having a comma in the URI.
    e.g.,

        /recording/_search/form1,form2,form3

    """

    # Create more phrases (and recordings) than queried forms.
    phrases = mommy.make_recipe('validation.phrase',
                                _quantity=MAX_RECORDING_QUERY_TERMS + 2)
    # We only want three of these word forms
    query_forms = [phrase.transcription for phrase in phrases][:MAX_RECORDING_QUERY_TERMS]

    # Ensure each phrase has a recording. Only a subset of these recordings
    # should be returned.
    speaker = mommy.make_recipe('validation.speaker')
    recordings = [mommy.make_recipe('validation.recording', phrase=phrase, speaker=speaker)
                  for phrase in phrases]

    response = client.get(reverse('validation:search_recordings',
                                  kwargs={'query': ','.join(query_forms)}))

    assert 'Access-Control-Allow-Origin' in response, "Missing requried CORS headers"

    matched_recordings = response.json()
    assert isinstance(matched_recordings, list)
    assert len(matched_recordings) == MAX_RECORDING_QUERY_TERMS
    for recording in matched_recordings:
        assert recording.get('wordform') in query_forms
        assert 'speaker' in recording.keys()
        assert recording.get('gender') in 'MF'
        assert recording.get('recording_url').startswith(('http://', 'https://'))
        assert recording.get('recording_url').endswith('.m4a')

    # The word forms in the response should match ALL of the word forms queried.
    assert set(r['wordform'] for r in matched_recordings) == set(query_forms)


@pytest.mark.django_db
def test_search_recording_not_found(client):
    # Create a valid recording, but make sure we never match it.
    recording = mommy.make_recipe('validation.recording')

    # Make the query never matches the only recording in the database:
    query = recording.phrase.transcription + 'h'
    response = client.get(reverse('validation:search_recordings',
                                  kwargs={'query': query}))

    recordings = response.json()
    assert 'Access-Control-Allow-Origin' in response, "Missing requried CORS headers"
    assert isinstance(recordings, list)
    assert len(recordings) == 0
    assert response.status_code == 404


@pytest.mark.django_db
def test_search_max_queries(client):
    # Create valid recordings, one per phrase, but make too many of them.
    speaker = mommy.make_recipe('validation.speaker')
    phrases = mommy.make_recipe('validation.phrase',
                                _quantity=MAX_RECORDING_QUERY_TERMS + 1)
    recordings = [
        mommy.make_recipe('validation.recording', speaker=speaker, phrase=phrase)
        for phrase in phrases
    ]

    # Try fetching the maximum
    query = ','.join(phrase.transcription for phrase in phrases[:MAX_RECORDING_QUERY_TERMS])
    response = client.get(reverse('validation:search_recordings',
                                  kwargs={'query': query}))
    assert response.status_code == 200

    # Fetch them!
    query = ','.join(phrase.transcription for phrase in phrases)
    response = client.get(reverse('validation:search_recordings',
                                  kwargs={'query': query}))

    # The request should be denied.
    assert 'Access-Control-Allow-Origin' in response, "Missing requried CORS headers"
    assert response.status_code == 414


@pytest.mark.django_db
def test_search_unique_word_forms(client):
    """
    Searching for a word form more than once in a single quert should return
    results as if the word form was requested only once.
    """
    # We need a valid phrase/recording
    recording = mommy.make_recipe('validation.recording')
    phrase = recording.phrase

    # The query will have the term more than once.
    assert MAX_RECORDING_QUERY_TERMS > 1
    query = ','.join(phrase.transcription for _ in
                     range(MAX_RECORDING_QUERY_TERMS))

    response = client.get(reverse('validation:search_recordings',
                                  kwargs={'query': query}))
    assert response.status_code == 200
    recordings = response.json()
    assert len(recordings) == 1
    assert recordings[0]['wordform'] == phrase.transcription


# ################################ Fixtures ################################ #

@pytest.fixture
def exported_recording(settings):
    """
    Yields a recording that has been physically saved on a storage medium.

    Yields a tuple of the Recording instance, and a bytes instance of the
    recording's transcoded audio.
    """
    recording = mommy.make_recipe('validation.recording')

    # Create a REAL audio recording, saved on disk.
    with TemporaryDirectory() as temp_dir_name:
        audio_dir = Path(temp_dir_name)

        # Temporarily override the audio directory name.
        settings.RECVAL_AUDIO_DIR = audio_dir
        audio = AudioSegment.empty()
        filename = audio_dir / f'{recording.id}.m4a'
        # Create an actual, bona fide M4A file.
        audio.export(os.fspath(filename), format='ipod')
        file_contents = filename.read_bytes()

        yield recording, file_contents
